# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add next_due_date columns

Revision ID: 28f2d0d0362
Revises: 2608242ad8ea
Create Date: 2014-08-16 00:40:28.003239

"""

# revision identifiers, used by Alembic.
revision = '28f2d0d0362'
down_revision = '2608242ad8ea'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('cycle_task_group_objects',
                  sa.Column('next_due_date', sa.Date(), nullable=True))
    op.add_column('cycle_task_groups',
                  sa.Column('next_due_date', sa.Date(), nullable=True))
    op.add_column('cycles', sa.Column(
        'next_due_date', sa.Date(), nullable=True))


def downgrade():
    op.drop_column('cycles', 'next_due_date')
    op.drop_column('cycle_task_groups', 'next_due_date')
    op.drop_column('cycle_task_group_objects', 'next_due_date')
