# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
Add Assignee roles to Task and Cycle Task types

Create Date: 2017-10-05 11:45:32.172481
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op


# revision identifiers, used by Alembic.
revision = '251191c050d0'
down_revision = '4131bd4a8a4d'


INSERT_TASK_ASSIGNEE = (
    """
       INSERT INTO access_control_roles
       (name, object_type, created_at, updated_at, mandatory, non_editable)
       SELECT 'Assignee', 'TaskGroupTask', NOW(), NOW(), 1, 1
       FROM access_control_roles
       WHERE NOT EXISTS(
          SELECT id FROM access_control_roles
          WHERE name = 'Assignee' AND object_type = 'TaskGroupTask'
       )
       LIMIT 1;
    """
)
INSERT_CYCLE_TASK_ASSIGNEE = (
    """
       INSERT INTO access_control_roles
       (name, object_type, created_at, updated_at, mandatory, non_editable)
       SELECT 'Assignee', 'CycleTaskGroupObjectTask', NOW(), NOW(), 1, 1
       FROM access_control_roles
       WHERE NOT EXISTS(
          SELECT id FROM access_control_roles
          WHERE name = 'Assignee'
            AND object_type = 'CycleTaskGroupObjectTask')
       LIMIT 1;
    """
)


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  op.execute(INSERT_TASK_ASSIGNEE)
  op.execute(INSERT_CYCLE_TASK_ASSIGNEE)


def downgrade():
  """Downgrade database schema and/or data back to the previous revision."""
