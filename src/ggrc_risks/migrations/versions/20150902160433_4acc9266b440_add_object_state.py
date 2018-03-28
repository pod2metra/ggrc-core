# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add object state

Revision ID: 4acc9266b440
Revises: 555130f0a817
Create Date: 2015-09-02 16:04:33.150812

"""

# revision identifiers, used by Alembic.
revision = '4acc9266b440'
down_revision = '555130f0a817'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.add_column('risks',
                  sa.Column('os_state', sa.String(length=250), nullable=False))
    op.add_column('threat_actors',
                  sa.Column('os_state', sa.String(length=250), nullable=False))


def downgrade():
    op.drop_column('threat_actors', 'os_state')
    op.drop_column('risks', 'os_state')
