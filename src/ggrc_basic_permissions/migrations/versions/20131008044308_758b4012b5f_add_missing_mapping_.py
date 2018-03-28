# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add missing mapping permissions.

Revision ID: 758b4012b5f
Revises: 3be0d9d2c9f8
Create Date: 2013-10-08 04:43:08.967577

"""

# revision identifiers, used by Alembic.
revision = '758b4012b5f'
down_revision = '3be0d9d2c9f8'

import json
import sqlalchemy as sa
from alembic import op
from datetime import datetime
from sqlalchemy.sql import table, column

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
)


def set_permissions(program_editor_objects):
    program_owner_objects = list(program_editor_objects)
    program_owner_objects.append('UserRole')

    current_datetime = datetime.now()
    op.execute(roles_table.update()\
        .values(
          permissions_json = json.dumps({
            'create': program_owner_objects,
            'read':   program_owner_objects,
            'update': program_owner_objects,
            'delete': program_owner_objects,
            }),
          updated_at = current_datetime,
          )\
        .where(roles_table.c.name == 'ProgramOwner'))
    op.execute(roles_table.update()\
        .values(
          permissions_json = json.dumps({
            'create': program_editor_objects,
            'read':   program_editor_objects,
            'update': program_editor_objects,
            'delete': program_editor_objects,
            }),
          updated_at = current_datetime)\
        .where(roles_table.c.name == 'ProgramEditor'))
    op.execute(roles_table.update()\
        .values(
          permissions_json = json.dumps({
            'create': [],
            'read': program_editor_objects,
            'update': [],
            'delete': [],
            }),
          updated_at = current_datetime)\
        .where(roles_table.c.name == 'ProgramReader'))


def upgrade():
    #create the context
    set_permissions([
        'Cycle',
        'ObjectDocument',
        'ObjectObjective',
        'ObjectPerson',
        'ObjectSection',
        'Program',
        'ProgramControl',
        'ProgramDirective',
        'Relationship',
    ])


def downgrade():
    set_permissions([
        'Cycle',
        'ObjectDocument',
        'ObjectPerson',
        'Program',
        'ProgramDirective',
        'Relationship',
    ])
