# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Set valid start_date and end_dates for annually

Create Date: 2017-09-27 13:25:42.962481
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import collections
import calendar
import datetime
from dateutil import relativedelta

from alembic import op

from ggrc_workflows.migrations.utils import wf_date_updater

# revision identifiers, used by Alembic.
revision = 'ab78b910268'
down_revision = 'ab76b910268'

ANNUALLY_SQL = (
    'SELECT w.id, w.next_cycle_start_date, w.status, w.recurrences, '
    't.id, t.relative_start_day, t.relative_start_month, '  # noqa: E131
    't.relative_end_day, t.relative_end_month, '
    'MAX(COALESCE(ct.start_date, CURDATE())) '
    'FROM workflows AS w '
    'JOIN task_groups AS tg ON tg.workflow_id = w.id '
    'JOIN task_group_tasks AS t ON t.task_group_id = tg.id '
    'LEFT JOIN cycle_task_group_object_tasks AS ct '
    'ON ct.task_group_task_id = t.id '
    'WHERE w.frequency = "annually" GROUP BY 1, 5;')

NOTIFICATION_OFFSET = {
    "month_workflow_starts_in": 1,
    "cycle_task_failed": -1,
}

YEAR = 2016


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    # pylint: disable=too-many-locals
    connection = op.get_bind()
    annually_tasks = connection.execute(ANNUALLY_SQL)

    tg_dates_dict = {}
    tg_wf = collections.defaultdict(set)
    ctg_wf = collections.defaultdict(set)
    wf_next_cycle_start_dates = {}
    wf_statuses = {}
    for (wf, wf_next_cycle_start_date, wf_status, wf_recur, tgt, start_day,
         start_month, end_day, end_month,
         last_task_start_date) in annually_tasks:

        if not (start_day and end_day and start_month and end_month):
            continue
        tg_wf[wf].add(tgt)
        ctg_wf[wf].add(last_task_start_date)
        tg_dates_dict[tgt] = (start_day, start_month, end_day, end_month)
        wf_next_cycle_start_dates[wf] = wf_next_cycle_start_date
        wf_statuses[wf] = (wf_status, wf_recur)

    today = datetime.date.today()
    group_days = collections.defaultdict(set)
    notification_to_update = collections.defaultdict(set)
    for wf, task_ids in tg_wf.iteritems():
        start_dates = []
        for task_id in task_ids:
            start_day, start_month, end_day, end_month = tg_dates_dict[task_id]
            _, max_start_day = calendar.monthrange(YEAR, start_month)
            _, max_end_day = calendar.monthrange(YEAR, end_month)
            start_date = datetime.date(YEAR, start_month,
                                       min(start_day, max_start_day))
            end_date = datetime.date(YEAR, end_month, min(
                end_day, max_end_day))
            while end_date < start_date:
                end_date += relativedelta.relativedelta(end_date, months=12)
            start_dates.append(start_date)
            group_days[(start_date, end_date)].add(task_id)
        repeat_multiplier, next_cycle_start_date = \
            wf_date_updater.get_next_cycle_start_date(
                min(start_dates),
                max([min(ctg_wf[wf]), today]),
                months=12
            )
        if wf_statuses[wf] == ("Active", 1):
            wf_date_updater.update_wf(op, repeat_multiplier,
                                      next_cycle_start_date, wf)
        if wf_statuses[wf] == ("Active", 1) and (
                next_cycle_start_date != wf_next_cycle_start_dates[wf]):
            print("Next cycle start date changed for "
                  "active workflow {} from {} to {}".format(
                      wf, wf_next_cycle_start_dates[wf],
                      next_cycle_start_date))
            for notification_type, offset in NOTIFICATION_OFFSET.iteritems():
                key = (notification_type,
                       next_cycle_start_date - datetime.timedelta(offset))
                notification_to_update[key].add(wf)
    wf_date_updater.update_notifications(op, notification_to_update)
    wf_date_updater.update_task_dates(op, group_days)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    pass
