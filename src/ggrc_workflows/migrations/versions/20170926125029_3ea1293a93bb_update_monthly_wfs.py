# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
update monthly wfs

Create Date: 2017-09-26 12:50:29.595921
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import collections
import datetime
from dateutil import relativedelta

from alembic import op

from ggrc_workflows.migrations.utils import wf_date_updater

# revision identifiers, used by Alembic.
revision = '3ea1293a93bb'
down_revision = '3ebe14ae9547'

MONTHLY_SQL = (
    'SELECT w.id, w.next_cycle_start_date, w.status, w.recurrences, '
    't.id, t.relative_start_day, t.relative_end_day, '  # noqa: E131
    'MAX(COALESCE(ct.start_date, CURDATE())) '
    'FROM workflows AS w '
    'JOIN task_groups AS tg ON tg.workflow_id = w.id '
    'JOIN task_group_tasks AS t ON t.task_group_id = tg.id '
    'LEFT JOIN cycle_task_group_object_tasks AS ct '
    'ON ct.task_group_task_id = t.id '
    'WHERE w.frequency = "monthly" GROUP BY 1, 5;')

NOTIFICATION_OFFSET = {
    "month_workflow_starts_in": 1,
    "cycle_task_failed": -1,
}

MONTH = 8
YEAR = 2017


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    # pylint: disable=too-many-locals
    ctg_wf = collections.defaultdict(set)  # collect last task start date
    tg_dates_dict = {}  # collect start and end days setup for task group
    tg_wf = collections.defaultdict(set)  # collect task groups for workflows
    wf_next_cycle_start_dates = {}
    wf_statuses = {}
    for row in op.get_bind().execute(MONTHLY_SQL):
        (wf, wf_next_cycle_start_date, wf_status, wf_recurrences, tgt,
         start_day, end_day, last_task_start_date) = row
        if not (start_day and end_day):
            continue
        wf_next_cycle_start_dates[wf] = wf_next_cycle_start_date
        wf_statuses[wf] = (wf_status, wf_recurrences)
        tg_wf[wf].add(tgt)
        ctg_wf[wf].add(last_task_start_date)
        tg_dates_dict[tgt] = (start_day, end_day)

    today = datetime.date.today()
    group_days = collections.defaultdict(set)
    notification_to_update = collections.defaultdict(set)
    for wf, task_ids in tg_wf.iteritems():
        start_dates = []
        for task_id in task_ids:
            start_date, end_date = [
                datetime.date(YEAR, MONTH, d) for d in tg_dates_dict[task_id]
            ]
            start_dates.append(start_date)
            if end_date < start_date:
                end_date += relativedelta.relativedelta(end_date, months=1)
            group_days[(start_date, end_date)].add(task_id)
        # min start_date is the setup start date of workflow
        # next cycle start date should be calculated based on that date
        repeat_multiplier, next_cycle_start_date = \
            wf_date_updater.get_next_cycle_start_date(
                min(start_dates),
                max([min(ctg_wf[wf]), today]),
                months=1)
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
