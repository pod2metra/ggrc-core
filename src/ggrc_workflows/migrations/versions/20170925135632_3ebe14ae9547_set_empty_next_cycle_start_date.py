# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Set empty next_cycle_start_date

Create Date: 2017-09-25 13:56:32.087965
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = '3ebe14ae9547'
down_revision = '4991c5731711'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.execute("UPDATE workflows, ( "
               "SELECT w.id "
               "FROM workflows AS w "
               "LEFT JOIN task_groups AS tg ON tg.workflow_id = w.id "
               "LEFT JOIN task_group_tasks AS t ON t.task_group_id = tg.id "
               "WHERE t.id IS NULL AND w.next_cycle_start_date IS NOT NULL "
               ") AS t "
               "SET workflows.next_cycle_start_date = NULL "
               "WHERE workflows.id = t.id;")


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    pass
