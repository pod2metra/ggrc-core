# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Clean up TaskGroupTask

Revision ID: 2b1ba26f2123
Revises: eab2ab6a0fc
Create Date: 2014-08-04 16:31:10.190834

"""

# revision identifiers, used by Alembic.
revision = '2b1ba26f2123'
down_revision = 'eab2ab6a0fc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # `status` was from Stateful mixin, no longer needed
    op.drop_column('task_group_tasks', 'status')

    # Remove linkage to `tasks` table, but this is weird because the index
    # enforcing the (`task_group_id`, `task_id`) uniqueness constraint is
    # reused for the `task_group_id` foreign key constraint, so we have to
    # remove the `task_group_id` constraint, then the uniqueness, then rebuild
    # the `task_group_id` foreign key constraint
    op.drop_constraint(
        'fk_task_group_tasks_task_id',
        table_name='task_group_tasks',
        type_='foreignkey')
    op.drop_constraint(
        'fk_task_group_tasks_task_group_id',
        table_name='task_group_tasks',
        type_='foreignkey')
    op.drop_constraint(
        'task_group_id', table_name='task_group_tasks', type_='unique')
    op.create_foreign_key('fk_task_group_tasks_task_group_id',
                          'task_group_tasks', 'task_groups', ['task_group_id'],
                          ['id'])
    op.drop_column('task_group_tasks', 'task_id')

    # Add indexes for other columns
    op.create_index(
        'fk_task_group_tasks_contact',
        'task_group_tasks', ['contact_id'],
        unique=False)

    # Ignore `Task.slug` uniqueness?
    #op.create_unique_constraint('uq_task_group_tasks', 'task_group_tasks', ['slug'])


def downgrade():
    pass
