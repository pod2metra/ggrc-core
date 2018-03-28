# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Remove cycle_task_group task_group key constraint

Revision ID: 53dcddf6c09e
Revises: 541f6ed93688
Create Date: 2014-09-12 15:08:37.646701

"""

# revision identifiers, used by Alembic.
revision = '53dcddf6c09e'
down_revision = '541f6ed93688'

from alembic import op


def upgrade():
    op.drop_constraint(
        'cycle_task_groups_ibfk_4', 'cycle_task_groups', type_='foreignkey')


def downgrade():
    # Warning: this will fail if the foreign key constraint fails
    op.create_foreign_key('cycle_task_groups_ibfk_4', 'cycle_task_groups',
                          'task_groups', ['task_group_id'], ['id'])
