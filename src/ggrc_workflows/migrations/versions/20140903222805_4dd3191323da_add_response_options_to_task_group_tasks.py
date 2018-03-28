# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add response options to task group tasks

Revision ID: 4dd3191323da
Revises: 4c6ce142b434
Create Date: 2014-09-03 22:28:05.079477

"""

# revision identifiers, used by Alembic.
revision = '4dd3191323da'
down_revision = '4c6ce142b434'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy.dialects import mysql


def upgrade():
    op.add_column('cycle_task_group_object_tasks',
                  sa.Column(
                      'response_options',
                      sa.Text(),
                      default="[]",
                      nullable=False))
    op.add_column('cycle_task_group_object_tasks',
                  sa.Column(
                      'selected_response_options',
                      sa.Text(),
                      default="[]",
                      nullable=False))
    op.add_column('cycle_task_group_object_tasks',
                  sa.Column(
                      'task_type', sa.String(length=250), nullable=False))
    op.add_column('task_group_tasks',
                  sa.Column(
                      'response_options',
                      sa.Text(),
                      default="[]",
                      nullable=False))
    op.add_column('task_group_tasks',
                  sa.Column(
                      'task_type', sa.String(length=250), nullable=False))

    ctgot_table = table(
        'cycle_task_group_object_tasks',
        column('id', sa.Integer),
        column('response_options', sa.Text),
        column('selected_response_options', sa.Text),
    )

    tgt_table = table(
        'task_group_tasks',
        column('id', sa.Integer),
        column('response_options', sa.Text),
    )

    op.execute(ctgot_table.update().values(
        response_options='[]',
        selected_response_options='[]',
    ))
    op.execute(tgt_table.update().values(response_options='[]', ))


def downgrade():
    op.drop_column('task_group_tasks', 'task_type')
    op.drop_column('task_group_tasks', 'response_options')
    op.drop_column('cycle_task_group_object_tasks', 'task_type')
    op.drop_column('cycle_task_group_object_tasks',
                   'selected_response_options')
    op.drop_column('cycle_task_group_object_tasks', 'response_options')
