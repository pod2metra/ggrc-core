# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Fix workflow cycle and group statuses

Create Date: 2017-07-31 19:38:56.374150
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = '396f47dcc433'
down_revision = '59aaa4750320'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.execute("""
      UPDATE cycle_task_groups
      SET status='Verified'
      WHERE id in (
          SELECT cycle_task_group_id
          FROM  cycle_task_group_object_tasks
          WHERE status = 'Verified')
      AND id not in (
          SELECT cycle_task_group_id
          FROM  cycle_task_group_object_tasks
          WHERE status <> 'Verified')
      AND status <> 'Verified'
  """)

    op.execute("""
      UPDATE cycle_task_groups
      SET status='Finished'
      WHERE id in (
          SELECT cycle_task_group_id
          FROM  cycle_task_group_object_tasks
          WHERE status = 'Finished')
      AND id not in (
          SELECT cycle_task_group_id
          FROM  cycle_task_group_object_tasks
          WHERE status  NOT IN ('Verified', 'Finished'))
      AND status <> 'Finished'
  """)

    op.execute("""
      UPDATE cycles
      SET status='Verified'
      WHERE id in (
          SELECT cycle_id
          FROM  cycle_task_groups
          WHERE status = 'Verified')
      AND id not in (
          SELECT cycle_id
          FROM  cycle_task_groups
          WHERE status <> 'Verified')
      AND status <> 'Verified'
  """)

    op.execute("""
      UPDATE cycles
      SET status='Finished'
      WHERE id in (
          SELECT cycle_id
          FROM  cycle_task_groups
          WHERE status = 'Finished')
      AND id not in (
          SELECT cycle_id
          FROM  cycle_task_groups
          WHERE status NOT IN ('Verified', 'Finished'))
      AND status <> 'Finished'
  """)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
