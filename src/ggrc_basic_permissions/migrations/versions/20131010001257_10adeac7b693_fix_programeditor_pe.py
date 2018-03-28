# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Fix ProgramEditor permissions

Revision ID: 10adeac7b693
Revises: 8f33d9bd2043
Create Date: 2013-10-10 00:12:57.391754

"""

# revision identifiers, used by Alembic.
revision = '10adeac7b693'
down_revision = '8f33d9bd2043'

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
    program_editor_delete_objects = list(program_editor_objects)
    program_editor_delete_objects.remove('Program')

    current_datetime = datetime.now()
    op.execute(roles_table.update()\
        .values(
          permissions_json = json.dumps({
            'create': program_editor_objects,
            'read':   program_editor_objects,
            'update': program_editor_objects,
            'delete': program_editor_delete_objects,
            }),
          updated_at = current_datetime)\
        .where(roles_table.c.name == 'ProgramEditor'))


def upgrade():
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
    pass
