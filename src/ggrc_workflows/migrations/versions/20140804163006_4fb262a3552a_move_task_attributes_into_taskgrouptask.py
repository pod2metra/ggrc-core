# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Move Task attributes into TaskGroupTask

Revision ID: 4fb262a3552a
Revises: 468290d5494f
Create Date: 2014-08-04 16:30:06.007514

"""

# revision identifiers, used by Alembic.
revision = '4fb262a3552a'
down_revision = '468290d5494f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('task_group_tasks',
                  sa.Column('contact_id', sa.Integer(), nullable=True))
    op.add_column('task_group_tasks',
                  sa.Column('description', sa.Text(), nullable=True))
    #op.add_column('task_group_tasks', sa.Column('slug', sa.String(length=250), nullable=False))
    op.add_column('task_group_tasks',
                  sa.Column('title', sa.String(length=250), nullable=False))


def downgrade():
    pass
