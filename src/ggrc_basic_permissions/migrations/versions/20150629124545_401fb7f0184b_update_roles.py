# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Update roles

Revision ID: 401fb7f0184b
Revises: 47218103cee5
Create Date: 2015-06-29 12:45:45.365535

"""

import sqlalchemy as sa
from alembic import op
from datetime import datetime
from sqlalchemy.sql import table, column, and_

# revision identifiers, used by Alembic.
revision = '401fb7f0184b'
down_revision = '47218103cee5'

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


def upgrade():
    op.execute("""
      UPDATE user_roles
      SET role_id = (SELECT id FROM roles WHERE name = 'ObjectEditor')
      WHERE role_id = (SELECT id FROM roles WHERE name = 'ProgramCreator');
  """)
    op.execute(roles_table.update().where(
        roles_table.c.name == 'ObjectEditor').values(
            name='Editor', description='Global Editor'))

    op.execute(roles_table.delete().where(
        and_(roles_table.c.name == 'ProgramCreator',
             roles_table.c.scope == 'System')))


def downgrade():
    op.execute(roles_table.insert().values(
        name='ProgramCreator',
        description='Program Creator',
        permissions_json="CODE DECLARED ROLE",
        scope='System'))
    op.execute(
        roles_table.update().where(roles_table.c.name == 'Editor').values(
            name='ObjectEditor', description='Global Editor'))
