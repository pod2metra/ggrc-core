# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Rename admin role.

Revision ID: 3adc42b4f6b9
Revises: 10adeac7b693
Create Date: 2013-10-10 22:13:16.470076

"""

# revision identifiers, used by Alembic.
revision = '3adc42b4f6b9'
down_revision = '10adeac7b693'

import json
import sqlalchemy as sa
from alembic import op
from datetime import datetime
from sqlalchemy.sql import table, column

roles_table = table(
    'roles',
    column('id', sa.Integer),
    column('name', sa.String),
    column('updated_at', sa.DateTime),
)


def upgrade():
    op.execute(roles_table.update()\
        .where(roles_table.c.name == 'System Administrator')\
        .values(name = 'gGRC Admin'))


def downgrade():
    op.execute(roles_table.update()\
        .where(roles_table.c.name == 'gGRC Admin')\
        .values(name = 'System Administrator'))
