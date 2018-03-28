# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add Creator role

Revision ID: 47218103cee5
Revises: 27432edbe6d4
Create Date: 2015-06-03 09:31:07.864860

"""

import sqlalchemy as sa
from alembic import op
from datetime import datetime
from sqlalchemy.sql import table, column, and_

# revision identifiers, used by Alembic.
revision = '47218103cee5'
down_revision = '27432edbe6d4'

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
    current_datetime = datetime.now()

    # Add the Creator role
    op.execute(roles_table.insert().values(
        name='Creator',
        description='Global creator',
        permissions_json="CODE DECLARED ROLE",
        created_at=current_datetime,
        updated_at=current_datetime,
        scope='System'))


def downgrade():
    op.execute(roles_table.delete().where(
        and_(roles_table.c.name == 'Creator',
             roles_table.c.scope == 'System')))
