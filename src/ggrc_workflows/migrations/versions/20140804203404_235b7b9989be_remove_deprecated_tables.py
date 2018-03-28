# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Remove deprecated tables

Revision ID: 235b7b9989be
Revises: 2b1ba26f2123
Create Date: 2014-08-04 20:34:04.786894

"""

# revision identifiers, used by Alembic.
revision = '235b7b9989be'
down_revision = '2b1ba26f2123'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # Drop now-unneeded tables
    op.drop_table('workflow_objects')
    op.drop_table('workflow_tasks')
    op.drop_table('tasks')


def downgrade():
    pass
