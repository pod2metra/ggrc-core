# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add Cycle.is_current

Revision ID: 1e40fcc473c1
Revises: 26d9c9c91542
Create Date: 2014-07-15 23:13:25.293355

"""

# revision identifiers, used by Alembic.
revision = '1e40fcc473c1'
down_revision = '26d9c9c91542'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

cycles_table = table('cycles', column('is_current', sa.Boolean),
                     column('status', sa.String))


def upgrade():
    op.add_column('cycles',
                  sa.Column('is_current', sa.Boolean(), nullable=False))

    op.execute(cycles_table.update().values(
        is_current=sa.case(
            [(cycles_table.c.status == 'InProgress', True)], else_=False)))


def downgrade():
    op.drop_column('cycles', 'is_current')
