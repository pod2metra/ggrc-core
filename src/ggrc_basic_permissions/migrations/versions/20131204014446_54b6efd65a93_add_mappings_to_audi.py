# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add mappings to Auditor role

Revision ID: 54b6efd65a93
Revises: 13b49798db19
Create Date: 2013-12-04 01:44:46.023974

"""

# revision identifiers, used by Alembic.
revision = '54b6efd65a93'
down_revision = '13b49798db19'

import sqlalchemy as sa
from alembic import op
from datetime import datetime
from sqlalchemy.sql import table, column, select
import json

roles_table = table('roles', column('id', sa.Integer), column(
    'name', sa.String), column('permissions_json', sa.String))

mapping_types = [
    'ObjectControl',
    'ObjectDocument',
    'ObjectObjective',
    'ObjectPerson',
    'ObjectSection',
    'Relationship',
]


def get_auditor_permissions():
    connection = op.get_bind()
    auditor_role = connection.execute(
        select([roles_table.c.id, roles_table.c.permissions_json])\
            .where(roles_table.c.name == 'Auditor')).fetchone()
    return json.loads(auditor_role.permissions_json)


def update_auditor_permissions(permissions):
    op.execute(roles_table\
        .update()\
        .values(permissions_json = json.dumps(permissions))\
        .where(roles_table.c.name == 'Auditor'))


def upgrade():
    permissions = get_auditor_permissions()
    permissions['read'].extend(mapping_types)
    update_auditor_permissions(permissions)


def downgrade():
    permissions = get_auditor_permissions()
    for resource_type in mapping_types:
        permissions['read'].remove(resource_type)
    update_auditor_permissions(permissions)
