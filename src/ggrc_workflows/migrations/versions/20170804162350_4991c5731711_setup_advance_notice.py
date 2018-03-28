# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
setup advance_notice

Create Date: 2017-08-04 16:23:50.724549
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = '4991c5731711'
down_revision = '47d42c67207f'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.execute("UPDATE notification_types set advance_notice=-1 "
               "where name in "
               "('cycle_start_failed', 'cycle_task_overdue');")
    op.execute("UPDATE notification_types set advance_notice=0 "
               "where name in "
               "('all_cycle_tasks_completed', 'cycle_task_declined');")


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    pass
