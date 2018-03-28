# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add workflow ACL roles

Create Date: 2017-11-26 00:00:00
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import datetime
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3355d60d65d8'
down_revision = '14b87f599ede'

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
WHERE object_type = 'Workflow'
"""


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.bulk_insert(ACR_TABLE, [{
        'name': 'Admin',
        'object_type': 'Workflow',
        'read': True,
        'update': True,
        'delete': True,
        'my_work': True,
        'created_at': datetime.datetime.now(),
        'updated_at': datetime.datetime.now(),
        'mandatory': True,
        'default_to_current_user': True,
        'non_editable': True,
        'internal': False
    }, {
        'name': 'Admin Mapped',
        'object_type': 'Workflow',
        'read': True,
        'update': True,
        'delete': True,
        'my_work': False,
        'created_at': datetime.datetime.now(),
        'updated_at': datetime.datetime.now(),
        'mandatory': False,
        'default_to_current_user': False,
        'non_editable': True,
        'internal': True
    }, {
        'name': 'Workflow Member',
        'object_type': 'Workflow',
        'read': True,
        'update': False,
        'delete': False,
        'my_work': False,
        'created_at': datetime.datetime.now(),
        'updated_at': datetime.datetime.now(),
        'mandatory': False,
        'default_to_current_user': False,
        'non_editable': True,
        'internal': False
    }, {
        'name': 'Workflow Member Mapped',
        'object_type': 'Workflow',
        'read': True,
        'update': False,
        'delete': False,
        'my_work': False,
        'created_at': datetime.datetime.now(),
        'updated_at': datetime.datetime.now(),
        'mandatory': False,
        'default_to_current_user': False,
        'non_editable': True,
        'internal': True
    }])


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.execute(DELETE_SQL)
