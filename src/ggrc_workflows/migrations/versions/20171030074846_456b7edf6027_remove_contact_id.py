# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Drop deprecated column 'contact_id' from 'task_group_tasks' and
'cycle_task_group_object_tasks'

Create Date: 2017-10-30 07:48:46.425098
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '456b7edf6027'
down_revision = '251191c050d0'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    # task_group_tasks:
    op.drop_index('fk_task_group_tasks_contact', 'task_group_tasks')
    op.drop_index('fk_task_group_tasks_secondary_contact', 'task_group_tasks')
    op.drop_column('task_group_tasks', 'contact_id')
    op.drop_column('task_group_tasks', 'secondary_contact_id')

    # cycle_task_group_object_tasks table:
    op.drop_constraint('cycle_task_group_object_tasks_ibfk_1',
                       'cycle_task_group_object_tasks', 'foreignkey')
    op.drop_index('fk_cycle_task_group_object_tasks_contact',
                  'cycle_task_group_object_tasks')
    op.drop_index('fk_cycle_task_group_object_tasks_secondary_contact',
                  'cycle_task_group_object_tasks')
    op.drop_column('cycle_task_group_object_tasks', 'contact_id')
    op.drop_column('cycle_task_group_object_tasks', 'secondary_contact_id')


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    # task_group_tasks:
    op.add_column('task_group_tasks',
                  sa.Column('contact_id', sa.Integer(), nullable=True))
    op.add_column('task_group_tasks',
                  sa.Column(
                      'secondary_contact_id', sa.Integer(), nullable=True))
    op.create_index(
        'fk_task_group_tasks_contact',
        'task_group_tasks', ['contact_id'],
        unique=False)
    op.create_index(
        'fk_task_group_tasks_secondary_contact',
        'task_group_tasks', ['secondary_contact_id'],
        unique=False)

    # cycle_task_group_object_tasks table:
    op.add_column('cycle_task_group_object_tasks',
                  sa.Column('contact_id', sa.Integer(), nullable=True))
    op.add_column('cycle_task_group_object_tasks',
                  sa.Column(
                      'secondary_contact_id', sa.Integer(), nullable=True))
    op.create_foreign_key("cycle_task_group_object_tasks_ibfk_1",
                          "cycle_task_group_object_tasks", "people",
                          ["contact_id"], ["id"])
    op.create_index(
        'fk_cycle_task_group_object_tasks_contact',
        'cycle_task_group_object_tasks', ['contact_id'],
        unique=False)
    op.create_index(
        'fk_cycle_task_group_object_tasks_secondary_contact',
        'cycle_task_group_object_tasks', ['secondary_contact_id'],
        unique=False)
