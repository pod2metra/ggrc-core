# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Handlers for workflow notifications.

This module contains all function needed for handling notification objects
needed by workflow notifications. The exposed functions are the entry points
for callback listeners.

exposed functions
    handle_workflow_modify,
    handle_cycle_task_group_object_task_put,
    handle_cycle_created,
    handle_cycle_modify,
    handle_cycle_task_status_change,
"""
import datetime
import collections

from sqlalchemy import inspect

from ggrc.models.notification import Notification

from ggrc_workflows import models
from ggrc_workflows.notification import pusher


def get_notif_name_by_wf(workflow):
    if not workflow.unit:
      return "cycle_task_due_in"
    return "{}_cycle_task_due_in".format(workflow.unit)


def handle_workflow_modify(sender, obj=None, src=None, service=None):
  """Update or add notifications on a workflow update."""
  if obj.status != obj.ACTIVE or obj.unit is None:
    return
  if not obj.next_cycle_start_date:
    obj.next_cycle_start_date = obj.min_task_start_date
  pusher.update_or_create_notifications(
      obj,
      obj.next_cycle_start_date,
      "{}_workflow_starts_in".format(obj.unit),
      "cycle_start_failed")
  query = pusher.get_notification_query(
      *list(obj.tasks),
      **{"notification_names": ["cycle_start_failed"]})
  notif_type = pusher.get_notification_type("cycle_start_failed")
  exist_task_ids = set(query.distinct(Notification.object_id))
  for task in obj.tasks:
    if task.id not in exist_task_ids:
      pusher.push(task, notif_type, task.start_date)


def handle_cycle_task_status_change(obj):
  if obj.is_done:
    query = pusher.get_notification_query(obj)
    query.delete(synchronize_session="fetch")
    # if all tasks are in inactive states then add notification to cycle
    if all(task.is_done for task in obj.cycle.cycle_task_group_object_tasks):
      pusher.update_or_create_notifications(
          obj.cycle,
          datetime.date.today(),
          "all_cycle_tasks_completed")
  else:
    pusher.get_notification_query(
        obj.cycle,
        **{"notification_names": ["all_cycle_tasks_completed"]}
    ).delete(synchronize_session="fetch")
    if obj.status == models.CycleTaskGroupObjectTask.DECLINED:
      pusher.update_or_create_notifications(
          obj, datetime.date.today(), "cycle_task_declined")
    pusher.update_or_create_notifications(
        obj,
        obj.end_date,
        get_notif_name_by_wf(obj.cycle.workflow),
        "cycle_task_due_today",
        "cycle_task_overdue")


def handle_cycle_task_group_object_task_put(obj):
  if inspect(obj).attrs._access_control_list.history.has_changes():
    types = ["cycle_task_reassigned", "cycle_created", "manual_cycle_created"]
    if not pusher.notification_exists_for(obj, notification_names=types):
      pusher.push(obj, pusher.get_notification_type("cycle_task_reassigned"))
  if inspect(obj).attrs.end_date.history.has_changes() and not obj.is_done:
    # if you change end date to past than overdue
    # notification should be send today
    pusher.update_or_create_notifications(
        obj,
        obj.end_date,
        get_notif_name_by_wf(obj.cycle.workflow),
        "cycle_task_due_today",
        "cycle_task_overdue")


def handle_cycle_modify(obj):
  if not inspect(obj).attrs.is_current.history.has_changes():
    return
  if not obj.is_current:
    # delete all notifications for cycle tasks
    pusher.get_notification_query(
        *list(obj.cycle_task_group_object_tasks)
    ).delete(synchronize_session="fetch")


def handle_cycle_created(obj, manually):
  today = datetime.date.today()
  if manually:
    create_notification = "manual_cycle_created"
  else:
    create_notification = "cycle_created"
  pusher.update_or_create_notifications(obj, today, create_notification)
  if not obj.is_current:
    return
  task_notif_name = get_notif_name_by_wf(obj.workflow)
  notification_names = [task_notif_name, create_notification,
                        "cycle_task_overdue", "cycle_task_due_today"]
  notif_dict = [pusher.get_notification_type(n) for n in notification_names]
  tasks = list(obj.cycle_task_group_object_tasks)
  query = pusher.get_notification_query(
      *tasks,
      **{"notification_names": notification_names})
  exists_notifications = collections.defaultdict(set)
  for notification in query:
    exists_notifications[notification.notification_type_id].add(
        notification.object_id)

  for notification_type in notif_dict:
    object_ids = exists_notifications[notification_type.id]
    repeatable_notification = (
        notification_type.name in pusher.REPEATABLE_NOTIFICATIONS
    )
    for task in tasks:
      if task.id in object_ids or task.is_done:
        continue
      if create_notification == notification_type.name:
        send_on = today
      else:
        send_on = task.end_date
      send_on -= datetime.timedelta(notification_type.advance_notice)
      if repeatable_notification:
        send_on = max(send_on, today)
      if send_on >= today:
        pusher.push(task, notification_type, send_on, repeatable_notification)
