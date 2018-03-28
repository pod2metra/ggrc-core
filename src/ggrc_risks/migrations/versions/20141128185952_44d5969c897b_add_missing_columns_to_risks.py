# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""add missing columns to risks

Revision ID: 44d5969c897b
Revises: 1347acbb4dc2
Create Date: 2014-11-28 18:59:52.290005

"""

# revision identifiers, used by Alembic.
revision = '44d5969c897b'
down_revision = '1347acbb4dc2'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('risks', sa.Column('start_date', sa.Date(), nullable=True))
    op.add_column('risks', sa.Column('end_date', sa.Date(), nullable=True))
    op.add_column('risks',
                  sa.Column('status', sa.String(length=250), nullable=True))


def downgrade():
    op.drop_column('risks', 'start_date')
    op.drop_column('risks', 'end_date')
    op.drop_column('risks', 'status')
