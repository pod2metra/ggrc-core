# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add CycleTaskGroupObject.object

Revision ID: 26d9c9c91542
Revises: 19a67dc67c3
Create Date: 2014-07-15 21:49:34.073412

"""

# revision identifiers, used by Alembic.
revision = '26d9c9c91542'
down_revision = '19a67dc67c3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('cycle_task_group_objects',
                  sa.Column('object_id', sa.Integer(), nullable=False))
    op.add_column('cycle_task_group_objects',
                  sa.Column(
                      'object_type', sa.String(length=250), nullable=False))

    op.execute('''
        UPDATE cycle_task_group_objects
            JOIN task_group_objects
                ON cycle_task_group_objects.task_group_object_id = task_group_objects.id
            SET
                cycle_task_group_objects.object_id = task_group_objects.object_id,
                cycle_task_group_objects.object_type = task_group_objects.object_type;
        ''')


def downgrade():
    op.drop_column('cycle_task_group_objects', 'object_type')
    op.drop_column('cycle_task_group_objects', 'object_id')
