# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Copy Task data into TaskGroupTask rows

Revision ID: eab2ab6a0fc
Revises: 4fb262a3552a
Create Date: 2014-08-04 16:30:35.560806

"""

# revision identifiers, used by Alembic.
revision = 'eab2ab6a0fc'
down_revision = '4fb262a3552a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column, select, insert, and_

tasks_table = table(
    'tasks',
    column('id', sa.Integer),
    column('title', sa.String),
    column('description', sa.Text),
)

task_group_tasks_table = table(
    'task_group_tasks',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('task_group_id', sa.Integer),
    column('task_id', sa.Integer),
    column('title', sa.String),
    column('description', sa.Text),
)


def upgrade():
    connection = op.get_bind()

    tasks_rows = connection.execute(
        select(
            [tasks_table.c.id, tasks_table.c.title,
             tasks_table.c.description]))
    tasks_by_id = {}
    for tasks_row in tasks_rows:
        tasks_by_id[tasks_row.id] = tasks_row

    task_group_tasks_rows = connection.execute(
        select([task_group_tasks_table.c.id,
                task_group_tasks_table.c.task_id]))
    for task_group_tasks_row in task_group_tasks_rows:
        task_id = task_group_tasks_row.task_id
        if task_id:
            tasks_row = tasks_by_id[task_id]

            op.execute(
                task_group_tasks_table.update()\
                    .values(
                      title=tasks_row.title,
                      description=tasks_row.description
                      )\
                    .where(
                      task_group_tasks_table.c.id == task_id
                      ))


def downgrade():
    pass
