# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add notes to Risk

Revision ID: 39518b8ea21d
Revises: 4acc9266b440
Create Date: 2015-09-17 20:15:27.852581

"""

# revision identifiers, used by Alembic.
revision = '39518b8ea21d'
down_revision = '4acc9266b440'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('risks', sa.Column('notes', sa.Text()))


def downgrade():
    op.drop_column('risks', 'notes')
