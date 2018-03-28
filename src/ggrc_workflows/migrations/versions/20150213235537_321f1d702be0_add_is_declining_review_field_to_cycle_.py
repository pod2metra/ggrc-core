# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add is_declining_review field to cycle_task_entry

Revision ID: 321f1d702be0
Revises: 11357eaaa6f7
Create Date: 2015-02-13 23:55:37.174611

"""

# revision identifiers, used by Alembic.
revision = '321f1d702be0'
down_revision = '527e6b728b44'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.add_column('cycle_task_entries',
                  sa.Column(
                      'is_declining_review', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('cycle_task_entries', 'is_declining_review')
