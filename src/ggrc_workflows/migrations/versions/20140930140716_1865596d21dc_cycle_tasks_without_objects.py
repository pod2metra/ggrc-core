# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Cycle tasks without objects

Revision ID: 1865596d21dc
Revises: 4dd3191323da
Create Date: 2014-09-30 14:07:16.347636

"""

# revision identifiers, used by Alembic.
revision = '1865596d21dc'
down_revision = '4dd3191323da'

from alembic import op
import sqlalchemy as sa


def upgrade():

    op.alter_column(
        'cycle_task_group_object_tasks',
        'cycle_task_group_object_id',
        existing_type=sa.Integer(),
        nullable=True)

    op.add_column('cycle_task_group_object_tasks',
                  sa.Column(
                      'cycle_task_group_id', sa.Integer(), nullable=False))

    op.execute("""
    UPDATE cycle_task_group_object_tasks
    SET cycle_task_group_id=(
      SELECT cycle_task_group_id
      FROM cycle_task_group_objects
      WHERE id=cycle_task_group_object_tasks.cycle_task_group_object_id
    )
  """)

    op.create_foreign_key("cycle_task_group_id",
                          "cycle_task_group_object_tasks", "cycle_task_groups",
                          ["cycle_task_group_id"], ["id"])


def downgrade():

    op.drop_constraint(
        "cycle_task_group_id",
        "cycle_task_group_object_tasks",
        type_="foreignkey")

    op.drop_column('cycle_task_group_object_tasks', 'cycle_task_group_id')

    op.alter_column(
        'cycle_task_group_object_tasks',
        'cycle_task_group_object_id',
        existing_type=sa.Integer(),
        nullable=False)
