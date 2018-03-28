# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Converts relative task group task dates to absolute ones to fit new
cycles calculation algorithm

Create Date: 2017-07-27 14:46:48.535970
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from datetime import date

import sqlalchemy as sa
from sqlalchemy.sql import and_

from alembic import op
from ggrc_workflows.migrations.utils.task_group_task_date_calculator import (
    annually_cycle_calculator,
    monthly_cycle_calculator,
    quarterly_cycle_calculator,
    weekly_cycle_calculator,
)

# revision identifiers, used by Alembic.
revision = '47d42c67207f'
down_revision = '416613a797e4'

CYCLE_CALCULATORS = {
    "weekly": weekly_cycle_calculator.WeeklyCycleCalculator(),
    "monthly": monthly_cycle_calculator.MonthlyCycleCalculator(),
    "quarterly": quarterly_cycle_calculator.QuarterlyCycleCalculator(),
    "annually": annually_cycle_calculator.AnnuallyCycleCalculator()
}

workflows_table = sa.sql.table(
    'workflows', sa.sql.column('id', sa.Integer),
    sa.sql.column('title', sa.String), sa.sql.column('frequency', sa.String),
    sa.sql.column('non_adjusted_next_cycle_start_date', sa.Date))
task_groups_table = sa.sql.table(
    'task_groups',
    sa.sql.column('id', sa.Integer),
    sa.sql.column('workflow_id', sa.Integer),
)
task_group_tasks_table = sa.sql.table(
    'task_group_tasks',
    sa.sql.column('id', sa.Integer),
    sa.sql.column('title', sa.String),
    sa.sql.column('task_group_id', sa.Integer),
    sa.sql.column('start_date', sa.Date),
    sa.sql.column('end_date', sa.Date),
    sa.sql.column('relative_start_day', sa.Integer),
    sa.sql.column('relative_start_month', sa.Integer),
    sa.sql.column('relative_end_day', sa.Integer),
    sa.sql.column('relative_end_month', sa.Integer),
)


# pylint: disable=unused-variable, too-many-locals
def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    today = date.today()
    connection = op.get_bind()

    data = connection.execute(
        sa.sql.select([
            task_group_tasks_table, task_groups_table, workflows_table
        ]).where(
            and_(
                task_group_tasks_table.c.task_group_id ==
                task_groups_table.c.id,
                task_groups_table.c.workflow_id == workflows_table.c.id,
                workflows_table.c.frequency != op.inline_literal('one_time'))))

    if data:
        res = []
        for (tgt_id, tgt_title, task_group_id, start_date, end_date,
             relative_start_day, relative_start_month, relative_end_day,
             relative_end_month, tg_id, workflow_id, wf_id, wf_title,
             frequency, non_adjusted_next_cycle_start_date) in data:
            base_date = non_adjusted_next_cycle_start_date or today
            cycle_calc = CYCLE_CALCULATORS.get(frequency)
            # while catching erroneous dates setup, migration fixes them by setting
            # start_ end_ dates to 'today'
            try:
                start_date, end_date, adj = cycle_calc.non_adjusted_task_date_range(
                    relative_start_day, relative_start_month, relative_end_day,
                    relative_end_month, base_date)
            except ValueError as e:
                print(u"Houston, we've had a problem. {} "
                      u"TaskGroupTask: id: {}, title: {}"
                      u"Workflow: id: {}, title: {}").format(
                          e.message, tgt_id, tgt_title, wf_id, wf_title)
                continue
            res.append((tgt_id, start_date, end_date))
            if adj:
                print(u"Task group task's date(s) was adjusted. "
                      u"TaskGroupTask: id: {}, title: {}"
                      u"Workflow: id: {}, title: {}").format(
                          tgt_id, tgt_title, wf_id, wf_title)

        if res:
            values = [
                "({}, '{}', '{}')".format(tgt_id, start_date, end_date)
                for tgt_id, start_date, end_date in res
            ]  # noqa
            op.execute("""
        INSERT INTO task_group_tasks (id, start_date, end_date)
        VALUES {}
        ON DUPLICATE KEY UPDATE start_date=VALUES(start_date),
                                end_date=VALUES(end_date);
      """.format(", ".join(values)))
        else:
            print(u"There is no data to update.")


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    pass
