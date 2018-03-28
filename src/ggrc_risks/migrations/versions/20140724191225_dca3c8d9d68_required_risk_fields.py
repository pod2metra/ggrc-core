# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Required Risk fields.

Revision ID: dca3c8d9d68
Revises: 5ab2b76012a6
Create Date: 2014-07-24 19:12:25.208137

"""

# revision identifiers, used by Alembic.
revision = 'dca3c8d9d68'
down_revision = '5ab2b76012a6'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.add_column('risks', sa.Column(
        'contact_id', sa.Integer(), nullable=True))
    op.add_column('risks', sa.Column('description', sa.Text(), nullable=False))


def downgrade():
    op.drop_column('risks', 'description')
    op.drop_column('risks', 'contact_id')
