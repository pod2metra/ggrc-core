# Copyright (C) 2017 Google Inc.
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

from ggrc_workflows.services import google_holidays


# revision identifiers, used by Alembic.
revision = '3ea1293a93bb'
down_revision = '3ebe14ae9547'

MONTHLY_SQL = (
    'SELECT w.id, t.id, t.relative_start_day, t.relative_end_day, '
           'MAX(COALESCE(ct.start_date, CURDATE())) '  # noqa: E131
    'FROM workflows AS w '
    'JOIN task_groups AS tg ON tg.workflow_id = w.id '
    'JOIN task_group_tasks AS t ON t.task_group_id = tg.id '
    'LEFT JOIN cycle_task_group_object_tasks AS ct '
           'ON ct.task_group_task_id = t.id '
    'WHERE w.frequency = "monthly" GROUP BY 1,2;'
)

UPDATE_TASKS_SQL = (
    "UPDATE task_group_tasks "
    "SET start_date='{start_date}', "
        "end_date='{end_date}' "  # noqa: E131
    "WHERE id IN ({ids})"
)

UPDATE_WF_SQL = (
    "UPDATE workflows "
    "SET repeat_multiplier='{repeat_multiplier}', "
        "next_cycle_start_date='{next_cycle_start_date}' "  # noqa: E131
    "WHERE id = {id}"
)

# hardcode the month and year,
MONTH = 8  # this is last 31 days month in the past
YEAR = 2017


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  # pylint: disable=too-many-locals
  ctg_wf = collections.defaultdict(set)  # collect last task start date
  tg_dates_dict = {}  # collect start and end days setup for task group
  tg_wf = collections.defaultdict(set)  # collect task groups for workflows
  holidays = google_holidays.GoogleHolidays()
  for row in op.get_bind().execute(MONTHLY_SQL):
    wf, tgt, start_day, end_day, last_task_start_date = row
    if not (start_day and end_day):
      continue
    tg_wf[wf].add(tgt)
    ctg_wf[wf].add(last_task_start_date)
    tg_dates_dict[tgt] = (start_day, end_day)

  today = datetime.date.today()
  # collect start and end days as key and task_group_ids as value that
  # required to be updated
  group_days = collections.defaultdict(set)
  for wf, task_ids in tg_wf.iteritems():
    # collect all start dates for workflow
    start_dates = []
    for task_id in task_ids:
      start_date, end_date = [datetime.date(YEAR, MONTH, d)
                              for d in tg_dates_dict[task_id]]
      start_dates.append(start_date)
      # end date should be bigger than start date
      # if it's not then we gess that end date in next month
      if end_date < start_date:
        end_date += relativedelta.relativedelta(end_date, months=1)
      group_days[(start_date, end_date)].add(task_id)
    # min start_date is the setup start date of workflow
    # next cycle start date should be calculated based on that date
    startup_next_cycle_start_date = min(start_dates)
    next_cycle_start_date = startup_next_cycle_start_date
    repeat_multiplier = 0
    # last cycle start date should be in min of started_dates in last cycle
    # last_cycle_date should be in future so compare it with today
    # this is required the next cycle start date will be in future
    # the reason is, we should have skipped cycle in priduction so we guess
    # that next cycles should be only in future and only if user manually start
    # a cycle then last_cycle_started_date will be in future
    last_cycle_started_date = max([min(ctg_wf[wf]), today])
    # calculate repeat_multiplier and next_cycle_start_date
    while next_cycle_start_date <= last_cycle_started_date:
      repeat_multiplier += 1
      next_cycle_start_date = (
          startup_next_cycle_start_date + relativedelta.relativedelta(
              startup_next_cycle_start_date,
              months=repeat_multiplier))
      # next cycle start date couldn't be on weekends or on holidays
      while (next_cycle_start_date.isoweekday() > 5 or
             next_cycle_start_date in holidays):
        next_cycle_start_date -= relativedelta.relativedelta(days=1)
    # update workflow for valid new setup
    op.execute(
        UPDATE_WF_SQL.format(repeat_multiplier=repeat_multiplier,
                             next_cycle_start_date=next_cycle_start_date,
                             id=wf)
    )
  # update tasks setup dates
  for days, task_ids in group_days.iteritems():
    start_date, end_date = days
    op.execute(
        UPDATE_TASKS_SQL.format(start_date=start_date,
                                end_date=end_date,
                                ids=", ".join(str(i) for i in task_ids))
    )


def downgrade():
  """Downgrade database schema and/or data back to the previous revision."""
  pass
