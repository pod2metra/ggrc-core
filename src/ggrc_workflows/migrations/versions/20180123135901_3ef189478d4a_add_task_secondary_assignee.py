# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add task secondary assignee

Create Date: 2018-01-23 13:59:01.782831
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import datetime
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '3ef189478d4a'
down_revision = '58e0f07e174b'

ACR_TABLE = sa.sql.table(
    'access_control_roles',
    sa.sql.column('name', sa.String),
    sa.sql.column('object_type', sa.String),
    sa.sql.column('read', sa.Boolean),
    sa.sql.column('update', sa.Boolean),
    sa.sql.column('delete', sa.Boolean),
    sa.sql.column('my_work', sa.Boolean),
    sa.sql.column('created_at', sa.DateTime),
    sa.sql.column('updated_at', sa.DateTime),
    sa.sql.column('mandatory', sa.Boolean),
    sa.sql.column('default_to_current_user', sa.Boolean),
    sa.sql.column('non_editable', sa.Boolean),
    sa.sql.column('internal', sa.Boolean),
)

DELETE_SQL = """
DELETE FROM access_control_roles
WHERE name = 'Task Secondary Assignees'
"""


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.bulk_insert(ACR_TABLE, [{
        'name': 'Task Secondary Assignees',
        'object_type': 'TaskGroupTask',
        'read': True,
        'update': True,
        'delete': False,
        'my_work': False,
        'created_at': datetime.datetime.now(),
        'updated_at': datetime.datetime.now(),
        'mandatory': False,
        'default_to_current_user': False,
        'non_editable': True,
        'internal': False
    }, {
        'name': 'Task Secondary Assignees',
        'object_type': 'CycleTaskGroupObjectTask',
        'read': True,
        'update': True,
        'delete': False,
        'my_work': False,
        'created_at': datetime.datetime.now(),
        'updated_at': datetime.datetime.now(),
        'mandatory': False,
        'default_to_current_user': False,
        'non_editable': True,
        'internal': False
    }])


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.execute(DELETE_SQL)
