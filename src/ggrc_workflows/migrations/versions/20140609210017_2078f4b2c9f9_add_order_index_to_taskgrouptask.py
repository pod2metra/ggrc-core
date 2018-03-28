# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add order/index to TaskGroupTask

Revision ID: 2078f4b2c9f9
Revises: 8ca25af37c4
Create Date: 2014-06-09 21:00:17.361594

"""

# revision identifiers, used by Alembic.
revision = '2078f4b2c9f9'
down_revision = '8ca25af37c4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(u'task_group_tasks',
                  sa.Column(
                      u'sort_index', sa.String(length=250), nullable=False))
    op.execute('update task_group_tasks set sort_index = id')
    op.add_column(u'task_groups',
                  sa.Column(u'lock_task_order', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column(u'task_group_tasks', u'sort_index')
    op.drop_column(u'task_groups', u'lock_task_order')
