# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Remove delete program permission from ProgramEditor.

Revision ID: 1f865f61312
Revises: eab1d38baee
Create Date: 2013-12-06 19:26:11.875923

"""

# revision identifiers, used by Alembic.
revision = '1f865f61312'
down_revision = 'eab1d38baee'

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
    permissions = get_role_permissions('ProgramEditor')
    permissions['delete'].remove('Program')
    update_role_permissions('ProgramEditor', permissions)


def downgrade():
    permissions = get_role_permissions('ProgramEditor')
    permissions['delete'].append('Program')
    update_role_permissions('ProgramEditor', permissions)
