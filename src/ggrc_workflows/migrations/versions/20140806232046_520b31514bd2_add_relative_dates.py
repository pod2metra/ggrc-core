# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add relative dates

Revision ID: 520b31514bd2
Revises: 32221e9f330c
Create Date: 2014-08-06 23:20:46.059979

"""

# revision identifiers, used by Alembic.
revision = '520b31514bd2'
down_revision = '32221e9f330c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('task_group_tasks',
                  sa.Column('relative_end_day', sa.Integer(), nullable=True))
    op.add_column('task_group_tasks',
                  sa.Column('relative_end_month', sa.Integer(), nullable=True))
    op.add_column('task_group_tasks',
                  sa.Column('relative_start_day', sa.Integer(), nullable=True))
    op.add_column('task_group_tasks',
                  sa.Column(
                      'relative_start_month', sa.Integer(), nullable=True))
    op.add_column('workflows',
                  sa.Column('next_cycle_start_date', sa.Date(), nullable=True))


def downgrade():
    op.drop_column('workflows', 'next_cycle_start_date')
    op.drop_column('task_group_tasks', 'relative_start_month')
    op.drop_column('task_group_tasks', 'relative_start_day')
    op.drop_column('task_group_tasks', 'relative_end_month')
    op.drop_column('task_group_tasks', 'relative_end_day')
