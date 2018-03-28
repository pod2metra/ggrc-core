# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add Admin role.

Revision ID: 3be0d9d2c9f8
Revises: 3148b80be376
Create Date: 2013-10-05 14:07:22.359908

"""

# revision identifiers, used by Alembic.
revision = '3be0d9d2c9f8'
down_revision = '3148b80be376'

import json
import sqlalchemy as sa
from alembic import op
from datetime import datetime
from sqlalchemy.sql import table, column, and_

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

contexts_table = table(
    'contexts',
    column('id', sa.Integer),
    column('name', sa.String),
    column('description', sa.Text),
)


def upgrade():
    current_datetime = datetime.now()

    # Add an explicit Admin context with id 0
    op.execute(contexts_table.insert().values(
        name='System Administration',
        description='Context for super-user permissions.',
    ))
    # Insert with id set seems to fail on mysql due to auto-incremented id.
    # force it after the fact.
    op.execute(contexts_table.update().values(id=0).where(
        contexts_table.c.name == 'System Administration'))

    # Add the System Administrator role
    op.execute(roles_table.insert().values(
        name='System Administrator',
        description='gGRC System Administrator with super-user privileges',
        permissions_json=json.dumps({
            '__GGRC_ADMIN__': ['__GGRC_ALL__'],
        }),
        created_at=current_datetime,
        updated_at=current_datetime,
        scope='Admin'))


def downgrade():
    op.execute(roles_table.delete().where(
        and_(roles_table.c.name == 'System Administrator',
             roles_table.c.scope == 'Admin')))
    op.execute(contexts_table.delete().where(contexts_table.c.id == 0))
