# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Help permissions

Revision ID: eab1d38baee
Revises: 54b6efd65a93
Create Date: 2013-12-04 23:25:42.313943

"""

# revision identifiers, used by Alembic.
revision = 'eab1d38baee'
down_revision = '54b6efd65a93'

import sqlalchemy as sa
from alembic import op
from datetime import datetime
from sqlalchemy.sql import table, column, select
import json

roles_table = table('roles', column('id', sa.Integer), column(
    'name', sa.String), column('permissions_json', sa.String))


def get_role_permissions(role):
    connection = op.get_bind()
    role = connection.execute(
        select([roles_table.c.permissions_json])\
            .where(roles_table.c.name == role)).fetchone()
    return json.loads(role.permissions_json)


def update_role_permissions(role, permissions):
    op.execute(roles_table\
        .update()\
        .values(permissions_json = json.dumps(permissions))\
        .where(roles_table.c.name == role))


def upgrade():
    permissions = get_role_permissions('ObjectEditor')
    permission_filter = \
        lambda item: isinstance(item, str)\
          or isinstance(item, unicode)\
          or item['type'] != 'Help'
    permissions['create'].remove('Help')
    permissions['update'] = filter(permission_filter, permissions['update'])
    permissions['delete'] = filter(permission_filter, permissions['delete'])
    update_role_permissions('ObjectEditor', permissions)


def downgrade():
    permissions = get_role_permissions('ObjectEditor')
    help_permissions = {
        'terms': {
            'list_property': 'owners',
            'value': '$current_user',
        },
        'type': 'Help',
        'condition': 'contains',
    }
    permissions['create'].append('Help')
    permissions['update'].append(help_permissions)
    permissions['delete'].append(help_permissions)
    update_role_permissions('ObjectEditor', permissions)
