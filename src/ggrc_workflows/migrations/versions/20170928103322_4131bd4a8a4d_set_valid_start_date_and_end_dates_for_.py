# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Set valid start_date and end_dates for weekly

Create Date: 2017-09-28 10:33:22.595314
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import collections
import datetime

from alembic import op

from ggrc_workflows.migrations.utils import wf_date_updater

# revision identifiers, used by Alembic.
revision = '4131bd4a8a4d'
down_revision = 'ab78b910268'

MONTH = 8
YEAR = 2017
DAYS = {
    1: datetime.date(YEAR, MONTH, 7),
    2: datetime.date(YEAR, MONTH, 8),
    3: datetime.date(YEAR, MONTH, 9),
    4: datetime.date(YEAR, MONTH, 10),
    5: datetime.date(YEAR, MONTH, 11),
}
WEEK_DELTA = datetime.timedelta(7)

WEEKLY_SQL = (
    'SELECT w.id, w.next_cycle_start_date, w.status, w.recurrences, '
    't.id, t.relative_start_day, t.relative_end_day, '  # noqa: E131
    'MAX(COALESCE(ct.start_date, CURDATE())) '
    'FROM workflows AS w '
    'JOIN task_groups AS tg ON tg.workflow_id = w.id '
    'JOIN task_group_tasks AS t ON t.task_group_id = tg.id '
    'LEFT JOIN cycle_task_group_object_tasks AS ct '
    'ON ct.task_group_task_id = t.id '
    'WHERE w.frequency = "weekly" GROUP BY 1, 5;')

NOTIFICATION_OFFSET = {
    "week_workflow_starts_in": 1,
    "cycle_task_failed": -1,
}


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    # pylint: disable=too-many-locals
    week_tasks = op.get_bind().execute(WEEKLY_SQL)
    ctg_wf = collections.defaultdict(set)
    group_days = collections.defaultdict(set)

    notification_to_update = collections.defaultdict(set)
    tg_dates_dict = {}
    tg_wf = collections.defaultdict(set)
    today = datetime.date.today()
    wf_next_cycle_start_dates = {}
    wf_statuses = {}
    for (wf, wf_next_cycle_start_date, wf_status, w_recur, tgt, start_day,
         end_day, last_task_start_date) in week_tasks:
        if not (start_day and end_day):
            continue
        ctg_wf[wf].add(last_task_start_date)
        tg_dates_dict[tgt] = (start_day, end_day)
        tg_wf[wf].add(tgt)
        wf_next_cycle_start_dates[wf] = wf_next_cycle_start_date
        wf_statuses[wf] = (wf_status, w_recur)

    for wf, task_ids in tg_wf.iteritems():
        start_dates = []
        for task_id in task_ids:
            start_day, end_day = tg_dates_dict[task_id]
            start_date = DAYS[start_day]
            start_dates.append(start_date)
            end_date = DAYS[end_day]
            if end_date < start_date:
                end_date += WEEK_DELTA
            group_days[(start_date, end_date)].add(task_id)
        repeat_multiplier, next_cycle_start_date = \
            wf_date_updater.get_next_cycle_start_date(
                min(start_dates),
                max([min(ctg_wf[wf]), today]),
                days=7
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
