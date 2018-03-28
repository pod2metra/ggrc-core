# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add sort index to task_groups and cycle_task_groups

Revision ID: 468290d5494f
Revises: 1f1ab1d371b6
Create Date: 2014-07-25 08:25:39.074611

"""

# revision identifiers, used by Alembic.
revision = '468290d5494f'
down_revision = '1f1ab1d371b6'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column, select


def _set_sort_index(table_1, table_1_id, table_2):

    connection = op.get_bind()

    rows_1 = connection.execute(select([table_1.c.id]))

    for row_1 in rows_1:
        rows_2 = connection.execute(
            select([table_2.c.id, table_2.c.sort_index])
            .where(table_2.c[table_1_id] == row_1.id))
        from decimal import Decimal
        max_index = Decimal(9007199254740991.0)
        current_index = max_index / 2
        for row_2 in rows_2:
            op.execute(table_2.update().values(sort_index=str(current_index))
                       .where(table_2.c.id == row_2.id))
            current_index = (current_index + max_index) / 2


def upgrade():
    op.add_column('task_groups',
                  sa.Column(
                      'sort_index', sa.String(length=250), nullable=False))
    op.add_column('cycle_task_groups',
                  sa.Column(
                      'sort_index', sa.String(length=250), nullable=False))

    workflows_table = table('workflows', column('id', sa.Integer))

    task_groups_table = table(
        'task_groups',
        column('id', sa.Integer),
        column('sort_index', sa.String),
        column('workflow_id', sa.Integer),
    )

    cycles_table = table(
        'cycles',
        column('id', sa.Integer),
        column('sort_index', sa.String),
        column('workflow_id', sa.Integer),
    )

    cycle_task_groups_table = table(
        'cycle_task_groups',
        column('id', sa.Integer),
        column('sort_index', sa.String),
        column('cycle_id', sa.Integer),
    )

    _set_sort_index(workflows_table, 'workflow_id', task_groups_table)
    _set_sort_index(cycles_table, 'cycle_id', cycle_task_groups_table)


def downgrade():
    op.drop_column('cycle_task_groups', 'sort_index')
    op.drop_column('task_groups', 'sort_index')
