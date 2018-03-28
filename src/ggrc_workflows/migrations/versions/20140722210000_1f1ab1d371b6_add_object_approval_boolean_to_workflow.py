# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add object approval boolean to workflow

Revision ID: 1f1ab1d371b6
Revises: 4b3316aa1acf
Create Date: 2014-07-22 21:00:00.00000

"""

# revision identifiers, used by Alembic.
revision = '1f1ab1d371b6'
down_revision = '4b3316aa1acf'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.add_column('workflows',
                  sa.Column('object_approval', sa.Boolean(), nullable=False))


def downgrade():
    op.drop_column('workflows', 'object_approval')
