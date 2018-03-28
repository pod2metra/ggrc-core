# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Utils required for migration to fix start and end dates for tasks."""
from dateutil import relativedelta

from ggrc_workflows.migrations.utils.task_group_task_date_calculator import (
    google_holidays)

# pylint: disable=invalid-name

UPDATE_NOTIFICATIONS = (
    "UPDATE notifications as n "
    "JOIN notification_types as t on n.notification_type_id = t.id "
    "SET send_on = '{send_on}' "
    "where n.object_type='Workflow' and "
    "n.object_id in ({ids}) and "  # noqa: E131
    "sent_at is Null and "
    "t.name = '{notification_name}'")

UPDATE_TASKS_SQL = (
    "UPDATE task_group_tasks "
    "SET start_date='{start_date}', "
    "end_date='{end_date}' "  # noqa: E131
    "WHERE id IN ({ids})")

UPDATE_WF_SQL = (
    "UPDATE workflows "
    "SET repeat_multiplier='{repeat_multiplier}', "
    "next_cycle_start_date='{next_cycle_start_date}' "  # noqa: E131
    "WHERE id = {id}")


def update_notifications(op, notification_to_update):
    """Update notifications for new date """
    for key, wfs in notification_to_update.iteritems():
        notification_type, send_on = key
        op.execute(
            UPDATE_NOTIFICATIONS.format(
                send_on=send_on,
                ids=", ".join(str(i) for i in wfs),
                notification_name=notification_type))


def update_task_dates(op, group_days):
    """update tasks setup dates"""
    for days, task_ids in group_days.iteritems():
        start_date, end_date = days
        op.execute(
            UPDATE_TASKS_SQL.format(
                start_date=start_date,
                end_date=end_date,
                ids=", ".join(str(i) for i in task_ids)))


def update_wf(op, repeat_multiplier, next_cycle_start_date, wf):
    op.execute(
        UPDATE_WF_SQL.format(
            repeat_multiplier=repeat_multiplier,
            next_cycle_start_date=next_cycle_start_date,
            id=wf))


def get_next_cycle_start_date(startup_next_cycle_start_date,
                              last_cycle_started_date,
                              months=0,
                              days=0):
    """last cycle start date should be in min of started_dates in last cycle
  last_cycle_date should be in future so compare it with today
  this is required the next cycle start date will be in future
  the reason is, we should have skipped cycle in priduction so we guess
  that next cycles should be only in future and only if user manually start
  a cycle then last_cycle_started_date will be in future
  calculate repeat_multiplier and next_cycle_start_date"""
    holidays = google_holidays.GoogleHolidays()
    repeat_multiplier = 0
    next_cycle_start_date = startup_next_cycle_start_date
    while next_cycle_start_date <= last_cycle_started_date:
        repeat_multiplier += 1
        next_cycle_start_date = (
            startup_next_cycle_start_date + relativedelta.relativedelta(
                startup_next_cycle_start_date,
                months=months * repeat_multiplier,
                days=days * repeat_multiplier))
        # next cycle start date couldn't be on weekends or on holidays
        while (next_cycle_start_date.isoweekday() > 5
               or next_cycle_start_date in holidays):
            next_cycle_start_date -= relativedelta.relativedelta(days=1)
    return repeat_multiplier, next_cycle_start_date
