# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Rename admin role from gGRC Admin to Administrator.

Create Date: 2016-06-03 12:02:09.438599
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = 'c9218e757bc'
down_revision = '4d5180ab1b42'

roles_table = table(
    'roles',
    column('id', sa.Integer),
    column('name', sa.String),
    column('updated_at', sa.DateTime),
    column('description', sa.Text),
)


def upgrade():
    op.execute(roles_table.update().where(roles_table.c.name == 'gGRC Admin')
               .values(
                   name='Administrator',
                   description='System Administrator with super-user '
                   'privileges'))


def downgrade():
    op.execute(
        roles_table.update().where(roles_table.c.name == 'Administrator')
        .values(
            name='gGRC Admin',
            description='gGRC System Administrator with super-user '
            'privileges'))
