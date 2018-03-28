# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Titles for Risks.

Revision ID: 5ab2b76012a6
Revises: 113eb68585b7
Create Date: 2014-07-23 03:39:54.105011

"""

# revision identifiers, used by Alembic.
revision = '5ab2b76012a6'
down_revision = '113eb68585b7'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.add_column('risks',
                  sa.Column('title', sa.String(length=250), nullable=False))
    op.create_unique_constraint('uq_t_risks', 'risks', ['title'])


def downgrade():
    op.drop_column('risks', 'title')
