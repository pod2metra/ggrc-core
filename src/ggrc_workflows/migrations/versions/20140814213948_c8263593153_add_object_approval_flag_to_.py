# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add object_approval flag to taskgrouptask

Revision ID: c8263593153
Revises: 468290d5494f
Create Date: 2014-08-01 21:39:48.857784

"""

# revision identifiers, used by Alembic.
revision = 'c8263593153'
down_revision = '520b31514bd2'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('task_group_tasks',
                  sa.Column('object_approval', sa.Boolean(), nullable=False))
    op.execute('update task_group_tasks tgt, task_groups tg, ' +
               'workflows wf set tgt.object_approval = true where ' +
               'tgt.task_group_id=tg.id and tg.workflow_id=wf.id and ' +
               "wf.object_approval=true and tgt.title like 'Object review %'")


def downgrade():
    op.drop_column('task_group_tasks', 'object_approval')
