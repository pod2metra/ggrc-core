# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add Cycle-related tables

Revision ID: 5ac75b9cbb64
Revises: 2078f4b2c9f9
Create Date: 2014-06-10 23:55:48.137814

"""

# revision identifiers, used by Alembic.
revision = '5ac75b9cbb64'
down_revision = '2078f4b2c9f9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('cycles', sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('workflow_id', sa.Integer(), nullable=False),
                    sa.Column('contact_id', sa.Integer(), nullable=True),
                    sa.Column('status', sa.String(length=250), nullable=True),
                    sa.Column('end_date', sa.Date(), nullable=True),
                    sa.Column('start_date', sa.Date(), nullable=True),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('title', sa.String(length=250), nullable=False),
                    sa.Column('slug', sa.String(length=250), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('modified_by_id', sa.Integer(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('context_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['contact_id'],
                        ['people.id'],
                    ),
                    sa.ForeignKeyConstraint(
                        ['context_id'],
                        ['contexts.id'],
                    ),
                    sa.ForeignKeyConstraint(
                        ['workflow_id'],
                        ['workflows.id'],
                    ), sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('slug', name='uq_cycles'))
    op.create_index(
        'fk_cycles_contact', 'cycles', ['contact_id'], unique=False)
    op.create_index(
        'fk_cycles_contexts', 'cycles', ['context_id'], unique=False)

    op.create_table('cycle_task_groups',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('cycle_id', sa.Integer(), nullable=False),
                    sa.Column('task_group_id', sa.Integer(), nullable=False),
                    sa.Column('contact_id', sa.Integer(), nullable=True),
                    sa.Column('status', sa.String(length=250), nullable=True),
                    sa.Column('end_date', sa.Date(), nullable=True),
                    sa.Column('start_date', sa.Date(), nullable=True),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('title', sa.String(length=250), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('modified_by_id', sa.Integer(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('context_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['contact_id'],
                        ['people.id'],
                    ),
                    sa.ForeignKeyConstraint(
                        ['context_id'],
                        ['contexts.id'],
                    ), sa.ForeignKeyConstraint(
                        ['cycle_id'],
                        ['cycles.id'],
                    ),
                    sa.ForeignKeyConstraint(
                        ['task_group_id'],
                        ['task_groups.id'],
                    ), sa.PrimaryKeyConstraint('id'))
    op.create_index(
        'fk_cycle_task_groups_contact',
        'cycle_task_groups', ['contact_id'],
        unique=False)
    op.create_index(
        'fk_cycle_task_groups_contexts',
        'cycle_task_groups', ['context_id'],
        unique=False)

    op.create_table('cycle_task_group_objects',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column(
                        'cycle_task_group_id', sa.Integer(), nullable=False),
                    sa.Column(
                        'task_group_object_id', sa.Integer(), nullable=False),
                    sa.Column('contact_id', sa.Integer(), nullable=True),
                    sa.Column('status', sa.String(length=250), nullable=True),
                    sa.Column('end_date', sa.Date(), nullable=True),
                    sa.Column('start_date', sa.Date(), nullable=True),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('title', sa.String(length=250), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('modified_by_id', sa.Integer(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('context_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['contact_id'],
                        ['people.id'],
                    ),
                    sa.ForeignKeyConstraint(
                        ['context_id'],
                        ['contexts.id'],
                    ),
                    sa.ForeignKeyConstraint(
                        ['cycle_task_group_id'],
                        ['cycle_task_groups.id'],
                    ),
                    sa.ForeignKeyConstraint(
                        ['task_group_object_id'],
                        ['task_group_objects.id'],
                    ), sa.PrimaryKeyConstraint('id'))
    op.create_index(
        'fk_cycle_task_group_objects_contact',
        'cycle_task_group_objects', ['contact_id'],
        unique=False)
    op.create_index(
        'fk_cycle_task_group_objects_contexts',
        'cycle_task_group_objects', ['context_id'],
        unique=False)

    op.create_table('cycle_task_group_object_tasks',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column(
                        'cycle_task_group_object_id',
                        sa.Integer(),
                        nullable=False),
                    sa.Column(
                        'task_group_task_id', sa.Integer(), nullable=False),
                    sa.Column('contact_id', sa.Integer(), nullable=True),
                    sa.Column('status', sa.String(length=250), nullable=True),
                    sa.Column('end_date', sa.Date(), nullable=True),
                    sa.Column('start_date', sa.Date(), nullable=True),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('title', sa.String(length=250), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('modified_by_id', sa.Integer(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('context_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['contact_id'],
                        ['people.id'],
                    ),
                    sa.ForeignKeyConstraint(
                        ['context_id'],
                        ['contexts.id'],
                    ),
                    sa.ForeignKeyConstraint(
                        ['cycle_task_group_object_id'],
                        ['cycle_task_group_objects.id'],
                    ),
                    sa.ForeignKeyConstraint(
                        ['task_group_task_id'],
                        ['task_group_tasks.id'],
                    ), sa.PrimaryKeyConstraint('id'))
    op.create_index(
        'fk_cycle_task_group_object_tasks_contact',
        'cycle_task_group_object_tasks', ['contact_id'],
        unique=False)
    op.create_index(
        'fk_cycle_task_group_object_tasks_contexts',
        'cycle_task_group_object_tasks', ['context_id'],
        unique=False)


def downgrade():
    op.drop_table('cycle_task_group_object_tasks')
    op.drop_table('cycle_task_group_objects')
    op.drop_table('cycle_task_groups')
    op.drop_table('cycles')
