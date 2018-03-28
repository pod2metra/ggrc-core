# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Constrain object page view permissions.

Revision ID: 4148ce155e54
Revises: 376a7b2fbf2f
Create Date: 2013-11-11 23:54:04.651351

"""

# revision identifiers, used by Alembic.
revision = '4148ce155e54'
down_revision = '37b63b122038'

import json
import sqlalchemy as sa
from alembic import op
from datetime import datetime
from sqlalchemy.sql import table, column, select

roles_table = table(
    'roles',
    column('id', sa.Integer),
    column('name', sa.String),
    column('permissions_json', sa.Text),
    column('description', sa.Text),
    column('modified_by_id', sa.Integer),
    column('created_at', sa.DateTime),
    column('updated_at', sa.DateTime),
    column('context_id', sa.Integer),
    column('scope', sa.String),
)

roles = [
    'ProgramCreator',
    'Reader',
    'ObjectEditor',
    'ProgramOwner',
    'ProgramEditor',
    'ProgramReader',
    'ProgramAuditOwner',
    'ProgramAuditEditor',
    'ProgramAuditReader',
    'Auditor',
    #'AuditorProgramReader',
]


def upgrade():
    connection = op.get_bind()
    for role_name in roles:
        role = connection.execute(select([roles_table.c.permissions_json])\
            .where(roles_table.c.name == role_name)
            ).fetchone()
        p = json.loads(role.permissions_json)
        p['view_object_page'] = ['__GGRC_ALL__']
        op.execute(roles_table.update()\
            .values(permissions_json=json.dumps(p))\
            .where(roles_table.c.name == role_name)
            )
    role = connection.execute(select([roles_table.c.permissions_json])\
        .where(roles_table.c.name == 'AuditorReader')
        ).fetchone()
    p = json.loads(role.permissions_json)
    p['view_object_page'] = []
    op.execute(roles_table.update()\
        .values(permissions_json=json.dumps(p))\
        .where(roles_table.c.name == 'AuditorReader')
        )


def downgrade():
    connection = op.get_bind()
    for role_name in roles:
        role = connection.execute(select([roles_table.c.permissions_json])\
            .where(roles_table.c.name == role_name)
            ).fetchone()
        p = json.loads(role.permissions_json)
        if 'view_object_page' in p:
            del p['view_object_page']
        op.execute(roles_table.update()\
            .values(permissions_json=json.dumps(p))\
            .where(roles_table.c.name == role_name)
            )
    role = connection.execute(select([roles_table.c.permissions_json])\
        .where(roles_table.c.name == 'AuditorReader')
        ).fetchone()
    p = json.loads(role.permissions_json)
    del p['view_object_page']
    op.execute(roles_table.update()\
        .values(permissions_json=json.dumps(p))\
        .where(roles_table.c.name == 'AuditorReader')
        )
