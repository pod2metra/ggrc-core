# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Drop create Program permission from ProgramOwner and ProgramEditor roles.

Revision ID: 40a621571ac7
Revises: 1a22bb208258
Create Date: 2013-12-05 22:12:46.273929

"""

# revision identifiers, used by Alembic.
revision = '40a621571ac7'
down_revision = '1a22bb208258'

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
    for role in ['ProgramOwner', 'ProgramEditor']:
        permissions = get_role_permissions(role)
        permissions['create'].remove('Program')
        update_role_permissions(role, permissions)


def downgrade():
    for role in ['ProgramOwner', 'ProgramEditor']:
        permissions = get_role_permissions(role)
        permissions['create'].append('Program')
        update_role_permissions(role, permissions)
