# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Update audit permissions.

Revision ID: 2785a204a673
Revises: c460b4f8cc3
Create Date: 2013-12-11 00:11:13.431124

"""

# revision identifiers, used by Alembic.
revision = '2785a204a673'
down_revision = 'c460b4f8cc3'

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
    additional_audit_objects = [
        'ObjectControl',
        'ObjectDocument',
        'ObjectObjective',
        'ObjectPerson',
        'ObjectSection',
        'Relationship',
        'Document',
        'Meeting',
    ]

    permissions = get_role_permissions('ProgramAuditReader')
    permissions['read'].extend(additional_audit_objects)
    update_role_permissions('ProgramAuditReader', permissions)

    permissions = get_role_permissions('ProgramAuditEditor')
    permissions['create'].extend(additional_audit_objects)
    permissions['read'].extend(additional_audit_objects)
    permissions['update'].extend(additional_audit_objects)
    permissions['delete'].extend(additional_audit_objects)
    update_role_permissions('ProgramAuditEditor', permissions)

    permissions = get_role_permissions('ProgramAuditOwner')
    permissions['create'].extend(additional_audit_objects)
    permissions['read'].extend(additional_audit_objects)
    permissions['update'].extend(additional_audit_objects)
    permissions['delete'].extend(additional_audit_objects)
    update_role_permissions('ProgramAuditOwner', permissions)


def downgrade():
    pass
