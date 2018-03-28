# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Change continuous frequency to one_time

Revision ID: 23f5b46fc4a3
Revises: 4d00d05f9e84
Create Date: 2014-08-22 17:30:20.558870

"""

# revision identifiers, used by Alembic.
revision = '23f5b46fc4a3'
down_revision = '4d00d05f9e84'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # workflows with cycles are active
    op.execute("""
      UPDATE workflows w
      SET w.frequency='one_time'
      WHERE w.frequency='continuous'
      """)


def downgrade():
    pass
