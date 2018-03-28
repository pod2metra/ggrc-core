# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Indexes on updated_at

Revision ID: 541f6ed93688
Revises: 23f5b46fc4a3
Create Date: 2014-09-12 23:01:33.170983

"""

# revision identifiers, used by Alembic.
revision = '541f6ed93688'
down_revision = '23f5b46fc4a3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index(
        'ix_cycle_task_entries_updated_at',
        'cycle_task_entries', ['updated_at'],
        unique=False)
    op.create_index(
        'ix_cycle_task_group_object_tasks_updated_at',
        'cycle_task_group_object_tasks', ['updated_at'],
        unique=False)
    op.create_index(
        'ix_cycle_task_group_objects_updated_at',
        'cycle_task_group_objects', ['updated_at'],
        unique=False)
    op.create_index(
        'ix_cycle_task_groups_updated_at',
        'cycle_task_groups', ['updated_at'],
        unique=False)
    op.create_index(
        'ix_cycles_updated_at', 'cycles', ['updated_at'], unique=False)
    op.create_index(
        'ix_task_group_objects_updated_at',
        'task_group_objects', ['updated_at'],
        unique=False)
    op.create_index(
        'ix_task_group_tasks_updated_at',
        'task_group_tasks', ['updated_at'],
        unique=False)
    op.create_index(
        'ix_task_groups_updated_at',
        'task_groups', ['updated_at'],
        unique=False)
    op.create_index(
        'ix_workflow_people_updated_at',
        'workflow_people', ['updated_at'],
        unique=False)
    op.create_index(
        'ix_workflows_updated_at', 'workflows', ['updated_at'], unique=False)


def downgrade():
    op.drop_index('ix_task_groups_updated_at', table_name='task_groups')
    op.drop_index(
        'ix_task_group_tasks_updated_at', table_name='task_group_tasks')
    op.drop_index(
        'ix_task_group_objects_updated_at', table_name='task_group_objects')
    op.drop_index('ix_cycles_updated_at', table_name='cycles')
    op.drop_index(
        'ix_cycle_task_groups_updated_at', table_name='cycle_task_groups')
    op.drop_index(
        'ix_cycle_task_group_objects_updated_at',
        table_name='cycle_task_group_objects')
    op.drop_index(
        'ix_cycle_task_group_object_tasks_updated_at',
        table_name='cycle_task_group_object_tasks')
    op.drop_index(
        'ix_cycle_task_entries_updated_at', table_name='cycle_task_entries')
    op.drop_index('ix_workflows_updated_at', table_name='workflows')
    op.drop_index(
        'ix_workflow_people_updated_at', table_name='workflow_people')
