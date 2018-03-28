# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Make sure cycle_task_groups always have status

Revision ID: 527e6b728b44
Revises: 11357eaaa6f7
Create Date: 2015-02-16 16:56:43.899103

"""

# revision identifiers, used by Alembic.
revision = '527e6b728b44'
down_revision = '11357eaaa6f7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("""
    UPDATE cycle_task_groups
    SET status='Assigned'
    WHERE status IS NULL
    """)


def downgrade():
    op.execute("""
    UPDATE cycle_task_groups
    SET status=NULL
    WHERE status='Assigned'
    """)
