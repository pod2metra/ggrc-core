# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add secondary contact columns

Revision ID: 529e4f55c8ed
Revises: 1865596d21dc
Create Date: 2015-01-22 21:20:00.347426

"""

# revision identifiers, used by Alembic.
revision = '529e4f55c8ed'
down_revision = '1865596d21dc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('cycle_task_group_object_tasks',
                  sa.Column(
                      'secondary_contact_id', sa.Integer(), nullable=True))
    op.create_index(
        'fk_cycle_task_group_object_tasks_secondary_contact',
        'cycle_task_group_object_tasks', ['secondary_contact_id'],
        unique=False)
    op.add_column('cycle_task_group_objects',
                  sa.Column(
                      'secondary_contact_id', sa.Integer(), nullable=True))
    op.create_index(
        'fk_cycle_task_group_objects_secondary_contact',
        'cycle_task_group_objects', ['secondary_contact_id'],
        unique=False)
    op.add_column('cycle_task_groups',
                  sa.Column(
                      'secondary_contact_id', sa.Integer(), nullable=True))
    op.create_index(
        'fk_cycle_task_groups_secondary_contact',
        'cycle_task_groups', ['secondary_contact_id'],
        unique=False)
    op.add_column('cycles',
                  sa.Column(
                      'secondary_contact_id', sa.Integer(), nullable=True))
    op.create_index(
        'fk_cycles_secondary_contact',
        'cycles', ['secondary_contact_id'],
        unique=False)
    op.add_column('task_group_tasks',
                  sa.Column(
                      'secondary_contact_id', sa.Integer(), nullable=True))
    op.create_index(
        'fk_task_group_tasks_secondary_contact',
        'task_group_tasks', ['secondary_contact_id'],
        unique=False)
    op.add_column('task_groups',
                  sa.Column(
                      'secondary_contact_id', sa.Integer(), nullable=True))
    op.create_index(
        'fk_task_groups_secondary_contact',
        'task_groups', ['secondary_contact_id'],
        unique=False)


def downgrade():
    op.drop_index('fk_task_groups_secondary_contact', table_name='task_groups')
    op.drop_column('task_groups', 'secondary_contact_id')
    op.drop_index(
        'fk_task_group_tasks_secondary_contact', table_name='task_group_tasks')
    op.drop_column('task_group_tasks', 'secondary_contact_id')
    op.drop_index('fk_cycles_secondary_contact', table_name='cycles')
    op.drop_column('cycles', 'secondary_contact_id')
    op.drop_index(
        'fk_cycle_task_groups_secondary_contact',
        table_name='cycle_task_groups')
    op.drop_column('cycle_task_groups', 'secondary_contact_id')
    op.drop_index(
        'fk_cycle_task_group_objects_secondary_contact',
        table_name='cycle_task_group_objects')
    op.drop_column('cycle_task_group_objects', 'secondary_contact_id')
    op.drop_index(
        'fk_cycle_task_group_object_tasks_secondary_contact',
        table_name='cycle_task_group_object_tasks')
    op.drop_column('cycle_task_group_object_tasks', 'secondary_contact_id')
