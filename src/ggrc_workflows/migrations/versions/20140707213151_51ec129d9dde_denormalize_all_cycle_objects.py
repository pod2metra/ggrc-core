# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Denormalize all cycle objects

Revision ID: 51ec129d9dde
Revises: 4157badaef20
Create Date: 2014-07-07 21:31:51.078897

"""

# revision identifiers, used by Alembic.
revision = '51ec129d9dde'
down_revision = '4157badaef20'

from alembic import op
import sqlalchemy as sa


def upgrade():

    op.add_column(u'cycle_task_entries',
                  sa.Column(u'cycle_id', sa.Integer(), nullable=False))
    op.add_column(u'cycle_task_group_objects',
                  sa.Column(u'cycle_id', sa.Integer(), nullable=False))
    op.add_column(u'cycle_task_group_object_tasks',
                  sa.Column(u'cycle_id', sa.Integer(), nullable=False))

    op.execute("""UPDATE cycle_task_group_objects SET cycle_id = (
       SELECT cycle_id FROM cycle_task_groups
        WHERE id=cycle_task_group_id);""")
    op.execute("""UPDATE cycle_task_group_object_tasks SET cycle_id = (
       SELECT cycle_id FROM cycle_task_group_objects
        WHERE id=cycle_task_group_object_id);""")
    op.execute("""UPDATE cycle_task_entries SET cycle_id = (
       SELECT cycle_id FROM cycle_task_group_object_tasks
        WHERE id=cycle_task_group_object_task_id);""")

    op.create_foreign_key('cycle_task_entries_cycle', 'cycle_task_entries',
                          'cycles', ['cycle_id'], ['id'])
    op.create_foreign_key('cycle_task_group_objects_cycle',
                          'cycle_task_group_objects', 'cycles', ['cycle_id'],
                          ['id'])
    op.create_foreign_key('cycle_task_group_object_tasks_cycle',
                          'cycle_task_group_object_tasks', 'cycles',
                          ['cycle_id'], ['id'])


def downgrade():
    op.drop_constraint(
        'cycle_task_entries_cycle', 'cycle_task_entries', type_='foreignkey')
    op.drop_constraint(
        'cycle_task_group_objects_cycle',
        'cycle_task_group_objects',
        type_='foreignkey')
    op.drop_constraint(
        'cycle_task_group_object_tasks_cycle',
        'cycle_task_group_object_tasks',
        type_='foreignkey')
    op.drop_column(u'cycle_task_entries', u'cycle_id')
    op.drop_column('cycle_task_group_objects', 'cycle_id')
    op.drop_column('cycle_task_group_object_tasks', 'cycle_id')
