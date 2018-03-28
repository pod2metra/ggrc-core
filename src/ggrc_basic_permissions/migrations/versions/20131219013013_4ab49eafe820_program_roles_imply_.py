# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Program roles imply Role read permission.

Revision ID: 4ab49eafe820
Revises: 3e08ed6b47b8
Create Date: 2013-12-19 01:30:13.706364

"""

# revision identifiers, used by Alembic.
revision = '4ab49eafe820'
down_revision = '3e08ed6b47b8'

import sqlalchemy as sa
from alembic import op
from datetime import datetime
from sqlalchemy.sql import table, column, select
import json

roles_table = table(
    'roles',
    column('id', sa.Integer),
    column('name', sa.String),
    column('permissions_json', sa.String),
    column('description', sa.Text),
    column('modified_by_id', sa.Integer),
    column('created_at', sa.DateTime),
    column('updated_at', sa.DateTime),
    column('context_id', sa.Integer),
    column('scope', sa.String),
)

programs_table = table(
    'programs',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
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


def get_program_basic_reader_role():
    connection = op.get_bind()
    return connection.execute(
        select([roles_table.c.id])\
            .where(roles_table.c.name == 'ProgramBasicReader')).fetchone()


def upgrade():
    current_time = datetime.now()
    op.execute(
        roles_table.insert().values(
          name='ProgramBasicReader',
          permissions_json=json.dumps({'read': ['Role', 'Person']}),
          description='Allow any user assigned a role in a program the ability to '\
            'read Role resources.',
          modified_by_id=1,
          created_at=current_time,
          updated_at=current_time,
          scope='Program Implied',
          ))
    connection = op.get_bind()
    roles = connection.execute(
        select([roles_table.c.id])\
            .where(roles_table.c.name.in_(
              ['ProgramReader', 'ProgramEditor', 'ProgramOwner'])))
    role_ids = [r.id for r in roles]
    program_basic_reader_role_id = get_program_basic_reader_role().id
    programs = connection.execute(select([programs_table.c.context_id]))
    program_context_ids = [p.context_id for p in programs]
    current_time = datetime.now()
    for program_context_id in program_context_ids:
        for role_id in role_ids:
            op.execute(role_implications_table.insert().values(
                source_context_id=program_context_id,
                context_id=None,
                source_role_id=role_id,
                role_id=program_basic_reader_role_id,
                modified_by_id=1,
                created_at=current_time,
                updated_at=current_time,
            ))


def downgrade():
    program_basic_reader_role_id = get_program_basic_reader_role().id
    op.execute(role_implications_table.delete().where(
        role_implications_table.c.role_id == program_basic_reader_role_id))
    op.execute(
        roles_table.delete().where(roles_table.c.name == 'ProgramBasicReader'))
