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
from ggrc.models import all_models
from ggrc import db

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


def done_tasks_notify(tasks):
  """Notification handling for task that moved in done state.

  It will
    - delete all notifications for done tasks
    - create notification for related cycle if all task in done state
  """
  if not tasks:
    return
  pusher.get_notification_query(*tasks).delete(synchronize_session="fetch")
  cycle_tasks_dict = collections.defaultdict(list)
  cycles_dict = {}
  task_ids = []
  for obj in tasks:
    cycle_tasks_dict[obj.cycle].append(obj)
    cycles_dict[obj.cycle.id] = obj.cycle
    task_ids.append(obj.id)

  task_query = all_models.CycleTaskGroupObjectTask.query.filter(
      all_models.CycleTaskGroupObjectTask.cycle_id.in_(cycles_dict.keys()),
      all_models.CycleTaskGroupObjectTask.id.notin_(task_ids),
  ).options(
      db.Load(
          all_models.CycleTaskGroupObjectTask
      ).undefer_group(
          "CycleTaskGroupObjectTask_complete"
      )
  ).all()
  for task in task_query:
    cycle_tasks_dict[cycles_dict[task.cycle_id]].append(task)

  done_cycles = [cycle for cycle, cycle_tasks in cycle_tasks_dict.iteritems()
                 if all(task.is_done for task in cycle_tasks)]
  pusher.create_notifications_for_objects("all_cycle_tasks_completed",
                                          datetime.date.today(),
                                          *done_cycles)


def not_done_tasks_notify(tasks):
  """Notification handling for tasks that moved to active state.

  It will
    - create notification for tasks if it's needed
    - delete all notifications for related cycles
  """
  if not tasks:
    return
  cycles = set()
  notification_send_at_tasks_dict = collections.defaultdict(list)
  notification_types = set()
  for task in tasks:
    cycles.add(task.cycle)
    if task.status == models.CycleTaskGroupObjectTask.DECLINED:
      notification_send_at_tasks_dict[
          ("cycle_task_declined", datetime.date.today())
      ].append(task)
      notification_types.add("cycle_task_declined")
    for n_type in [get_notif_name_by_wf(task.cycle.workflow),
                   "cycle_task_due_today",
                   "cycle_task_overdue"]:
      notification_send_at_tasks_dict[
          (n_type, task.end_date)
      ].append(task)
      notification_types.add(n_type)
  # delete all notifications for cycles about all tasks compleated and
  # all tasks notifications that required to be updated
  pusher.get_notification_query(
      *(list(cycles) + tasks),
      **{"notification_names": [
          "all_cycle_tasks_completed"
      ] + list(notification_types)}
  ).delete(
      synchronize_session="fetch"
  )
  notification_type_query = pusher.get_notification_types(*notification_types)
  notification_types_dict = {t.name: t for t in notification_type_query}
  for pair, pair_tasks in notification_send_at_tasks_dict.iteritems():
    notification_type_name, send_at = pair
    notification_type = notification_types_dict[notification_type_name]
    pusher.create_notifications_for_objects(notification_type,
                                            send_at,
                                            *pair_tasks)


def handle_cycle_task_status_change(*objs):
  """Notification handling for task status change."""
  done_tasks = []
  not_done_tasks = []
  for obj in objs:
    if obj.is_done:
      done_tasks.append(obj)
    else:
      not_done_tasks.append(obj)
  done_tasks_notify(done_tasks)
  not_done_tasks_notify(not_done_tasks)


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
  notification_names = [get_notif_name_by_wf(obj.workflow),
                        create_notification,
                        "cycle_task_overdue",
                        "cycle_task_due_today"]
  tasks = list(obj.cycle_task_group_object_tasks)
  query = pusher.get_notification_query(
      *tasks,
      **{"notification_names": notification_names})
  exists_notifications = collections.defaultdict(set)
  for notification in query:
    exists_notifications[notification.notification_type_id].add(
        notification.object_id)
  for notification_type in pusher.get_notification_types(*notification_names):
    object_ids = exists_notifications[notification_type.id]
    notify_tasks = [t for t in tasks if not (t.id in object_ids or t.is_done)]
    if create_notification == notification_type.name:
      pusher.create_notifications_for_objects(notification_type,
                                              today,
                                              *notify_tasks)
    else:
      for task in notify_tasks:
        pusher.create_notifications_for_objects(notification_type,
                                                task.end_date,
                                                task)
