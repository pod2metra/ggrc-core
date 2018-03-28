# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Remove prohibitive foreign key constraints

Revision ID: 32221e9f330c
Revises: 235b7b9989be
Create Date: 2014-08-04 20:34:36.697866

"""

# revision identifiers, used by Alembic.
revision = '32221e9f330c'
down_revision = '235b7b9989be'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_constraint(
        'uq_t_workflows', table_name='workflows', type_='unique')
    op.drop_constraint(
        'uq_t_task_groups', table_name='task_groups', type_='unique')
    op.drop_constraint(
        'cycle_task_group_object_tasks_ibfk_4',
        table_name='cycle_task_group_object_tasks',
        type_='foreignkey')
    op.drop_constraint(
        'cycle_task_group_objects_ibfk_4',
        table_name='cycle_task_group_objects',
        type_='foreignkey')


def downgrade():
    pass
