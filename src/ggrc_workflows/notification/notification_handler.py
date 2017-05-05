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
from datetime import timedelta
from datetime import datetime
from datetime import date

from sqlalchemy import and_
from sqlalchemy import or_
from sqlalchemy import inspect
from sqlalchemy.sql.expression import true

from ggrc import db
from ggrc.models.notification import Notification
from ggrc.models.notification import NotificationType
from ggrc.models.notification import (
    get_notification_type,
    has_unsent_notifications,
)

from ggrc_workflows.models.cycle_task_group_object_task import \
    CycleTaskGroupObjectTask


def handle_task_group_task(obj, notif_type=None):
  """Add notification entry for task group tasks.

  Args:
    obj: Instance of a model for which the notification should be scheduled.
    notif_type: The notification type for the scheduled notification.
  """
  if not notif_type:
    return

  if not has_unsent_notifications(obj, notif_type):
    start_date = obj.task_group.workflow.next_cycle_start_date
    send_on = start_date - timedelta(notif_type.advance_notice)
    add_notif(obj, notif_type, send_on)


def handle_workflow_modify(obj):
  """Update or add notifications on a workflow update."""
  if obj.status != "Active" or obj.frequency == "one_time":
    return

  if not obj.next_cycle_start_date:
    obj.next_cycle_start_date = date.today()

  notif_type = get_notification_type(
      "{}_workflow_starts_in".format(obj.frequency))
  if not has_unsent_notifications(obj):
    send_on = obj.next_cycle_start_date - timedelta(notif_type.advance_notice)
    add_notif(obj, notif_type, send_on)

    notif_type = get_notification_type("cycle_start_failed")
    add_notif(obj, notif_type, obj.next_cycle_start_date + timedelta(1))

  for task_group in obj.task_groups:
    for task_group_task in task_group.task_group_tasks:
      handle_task_group_task(task_group_task, notif_type)


def add_cycle_task_due_notifications(task):
  """Add notifications entries for cycle task due dates.

  Create notification entries: one for X days before the due date, one on the
  due date, and one for the days after ta task has become overdue.

  Args:
    task: CycleTaskGroupObjectTask instance to generate the notifications for.
  """
  if task.status == "Verified":
    return
  if not task.cycle_task_group.cycle.is_current:
    return

  notif_type = get_notification_type("{}_cycle_task_due_in".format(
      task.cycle_task_group.cycle.workflow.frequency))
  send_on = task.end_date - timedelta(notif_type.advance_notice)
  add_notif(task, notif_type, send_on)

  notif_type = get_notification_type("cycle_task_due_today")
  send_on = task.end_date - timedelta(notif_type.advance_notice)
  add_notif(task, notif_type, send_on)

  notif_type = get_notification_type("cycle_task_overdue")
  send_on = task.end_date + timedelta(1)
  add_notif(task, notif_type, send_on, repeating=True)


def add_cycle_task_notifications(obj, start_notif_type=None):
  """Add start and due  notification entries for cycle tasks."""
  add_notif(obj, start_notif_type, date.today())
  add_cycle_task_due_notifications(obj)


def add_cycle_task_reassigned_notification(obj):
  """Add or update notifications for reassigned cycle tasks."""
  # check if the current assignee already got the first notification
  result = db.session.query(Notification)\
      .join(NotificationType)\
      .filter(and_(Notification.object_id == obj.id,  # noqa
                   Notification.object_type == obj.type,
                   Notification.sent_at != None,
                   or_(NotificationType.name == "cycle_task_reassigned",
                       NotificationType.name == "cycle_created",
                       NotificationType.name == "manual_cycle_created",
                       )))

  if not db.session.query(result.exists()).one()[0]:
    return

  notif_type = get_notification_type("cycle_task_reassigned")
  add_notif(obj, notif_type)


def modify_cycle_task_notification(obj, notification_name):
  notif = db.session.query(Notification)\
      .join(NotificationType)\
      .filter(and_(Notification.object_id == obj.id,
                   Notification.object_type == obj.type,
                   or_(
                       Notification.sent_at.is_(None),
                       Notification.repeating == true()
                   ),
                   NotificationType.name == notification_name,
                   ))
  notif_type = get_notification_type(notification_name)
  send_on = datetime.combine(obj.end_date, datetime.min.time()) - timedelta(
      notif_type.advance_notice)
  today = datetime.combine(date.today(), datetime.min.time())
  if send_on >= today:
    # when cycle date is moved in the future, we update the current
    # notification or add a new one.
    notif = notif.first()
    if notif:
      notif.send_on = (datetime.combine(obj.end_date, datetime.min.time()) -
                       timedelta(notif.notification_type.advance_notice))
      db.session.add(notif)
    else:
      add_notif(obj, notif_type, send_on)
  else:
    # this should not be allowed, but if a cycle task is changed to a past
    # date, we remove the current pending notification if it exists
    for notif in notif.all():
      db.session.delete(notif)


def modify_cycle_task_overdue_notification(task):
  """Add or update the task's overdue notification.

  If an overdue notification already exists for the task, its date of sending
  is adjusted as needed. If such notification does not exist yet, it gets
  created.

  Args:
    task: The CycleTaskGroupObjectTask instance for which to update the overdue
          notifications.
  """
  notif = db.session.query(Notification)\
      .join(NotificationType)\
      .filter(
          (Notification.object_id == task.id) &
          (Notification.object_type == task.type) &
          (
              Notification.sent_at.is_(None) |
              (Notification.repeating == true())
          ) &
          (NotificationType.name == u"cycle_task_overdue"))

  notif_type = get_notification_type(u"cycle_task_overdue")
  send_on = datetime.combine(task.end_date, datetime.min.time()) + \
      timedelta(1)

  if notif.count() > 0:
    notif = notif.one()

    if notif.send_on == send_on:
      return  # nothing to do here...
    notif.send_on = send_on
    db.session.add(notif)
  else:
    # NOTE: The "task.id" check is to assure a notification is created for
    # existing task instances only, avoiding DB errors. Overdue notifications
    # for new tasks are handled and added elsewhere.
    if (
        task.id and task.status in CycleTaskGroupObjectTask.ACTIVE_STATES and
        task.cycle.is_current
    ):
      add_notif(task, notif_type, send_on, repeating=True)


def modify_cycle_task_end_date(obj):
  modify_cycle_task_notification(obj, "{}_cycle_task_due_in".format(
      obj.cycle_task_group.cycle.workflow.frequency))
  modify_cycle_task_notification(obj, "cycle_task_due_today")
  modify_cycle_task_overdue_notification(obj)


def check_all_cycle_tasks_finished(cycle):
  statuses = set([task.status for task in cycle.cycle_task_group_object_tasks])
  acceptable_statuses = set(['Verified'])
  return statuses.issubset(acceptable_statuses)


def handle_cycle_task_status_change(obj):
  if obj.status == "Declined":
    notif_type = get_notification_type("cycle_task_declined")
    add_notif(obj, notif_type)

  elif obj.status == "Verified":
    get_notification(obj).delete()

    cycle = obj.cycle_task_group.cycle
    if check_all_cycle_tasks_finished(cycle):
      notif_type = get_notification_type("all_cycle_tasks_completed")
      add_notif(cycle, notif_type)

  # NOTE: The only inactive state is "Verified", which is sufficiently handled
  # by the code above, thus we only need to handle active states
  if obj.status in CycleTaskGroupObjectTask.ACTIVE_STATES:
    modify_cycle_task_overdue_notification(obj)


def handle_cycle_task_group_object_task_put(obj):
  if inspect(obj).attrs.contact.history.has_changes():
    add_cycle_task_reassigned_notification(obj)

  history = inspect(obj).attrs.end_date.history
  if not history.has_changes():
    return

  # NOTE: A history might "detect" a change even if end_date was not changed
  # due to different data types, i.e.  date vs. datetime with the time part set
  # to zero. Example:
  #
  #   >>> datetime(2017, 5, 15, 0, 0) == date(2017, 5, 15)
  #   False
  #
  # We thus need to manually check both date values without the time part
  # in order to avoid unnecessary work and DB updates.
  old_date = history.deleted[0] if history.deleted else None
  new_date = history.added[0] if history.added else None

  if old_date is not None and new_date is not None:
    if isinstance(old_date, datetime):
      old_date = old_date.date()
    if isinstance(new_date, datetime):
      new_date = new_date.date()

    if old_date == new_date:
      return  # we have a false positive, no change actually occurred

  # the end date has actually changed, respond accordingly
  modify_cycle_task_end_date(obj)


def remove_all_cycle_task_notifications(obj):
  for cycle_task in obj.cycle_task_group_object_tasks:
    get_notification(cycle_task).delete()


def handle_cycle_modify(obj):
  if not obj.is_current:
    remove_all_cycle_task_notifications(obj)


def handle_cycle_created(obj):

  if not has_unsent_notifications(obj):
    notification_type = get_notification_type(
        "manual_cycle_created" if obj.manually_created else "cycle_created"
    )
    add_notif(obj, notification_type)

  for cycle_task_group in obj.cycle_task_groups:
    for task in cycle_task_group.cycle_task_group_tasks:
      add_cycle_task_notifications(task, notification_type)


def get_notification(obj):
  # maybe we shouldn't return different thigs here.
  return db.session.query(Notification).filter(
      Notification.object_id == obj.id,
      Notification.object_type == obj.type,
      or_(
          Notification.sent_at.is_(None),
          Notification.repeating == true(),
      ),
  )


def add_notif(obj, notif_type, send_on=None, repeating=False):
  if not send_on:
    send_on = date.today()
  notif = Notification(
      object_id=obj.id,
      object_type=obj.type,
      notification_type_id=notif_type.id,
      send_on=send_on,
      repeating=repeating,
  )
  db.session.add(notif)
