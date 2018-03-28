# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""ProgramCreator has ObjectEditor permissions.

Revision ID: 376a7b2fbf2f
Revises: 4838619603a
Create Date: 2013-11-04 23:16:38.407085

"""

# revision identifiers, used by Alembic.
revision = '376a7b2fbf2f'
down_revision = '904377398db'

import sqlalchemy as sa
from alembic import op
from datetime import datetime
from sqlalchemy.sql import table, column, select

roles_table = table(
    'roles',
    column('id', sa.Integer),
    column('name', sa.String),
)

role_implications_table = table(
    'role_implications',
    column('id', sa.Integer),
    column('source_context_id', sa.Integer),
    column('context_id', sa.Integer),
    column('source_role_id', sa.Integer),
    column('role_id', sa.Integer),
    column('modified_by_id', sa.Integer),
    column('created_at', sa.DateTime),
    column('updated_at', sa.DateTime),
)


def upgrade():
    connection = op.get_bind()
    program_creator_role = connection.execute(
        select([roles_table.c.id])\
          .where(roles_table.c.name == 'ProgramCreator')\
          .limit(1)).fetchone()
    object_editor_role = connection.execute(
        select([roles_table.c.id])\
          .where(roles_table.c.name == 'ObjectEditor')\
          .limit(1)).fetchone()
    current_datetime = datetime.now()
    op.execute(role_implications_table.insert().values(
        source_context_id=None,
        context_id=None,
        source_role_id=program_creator_role['id'],
        role_id=object_editor_role['id'],
        modified_by_id=1,
        created_at=current_datetime,
        updated_at=current_datetime,
    ))


def downgrade():
    pass
