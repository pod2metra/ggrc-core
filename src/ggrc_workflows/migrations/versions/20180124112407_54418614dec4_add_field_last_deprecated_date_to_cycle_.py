# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
add field last_deprecated_date to cycle_task_group_object_tasks

Create Date: 2018-01-24 11:24:07.291724
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '54418614dec4'
down_revision = '3ef189478d4a'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.add_column('cycle_task_group_object_tasks',
                  sa.Column('last_deprecated_date', sa.Date))


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_column('cycle_task_group_object_tasks', 'last_deprecated_date')
