# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add program id to risk asssessment

Revision ID: 51f2bcff9bcd
Revises: 29003bebd436
Create Date: 2014-07-17 18:47:57.202120

"""

# revision identifiers, used by Alembic.
revision = '51f2bcff9bcd'
down_revision = '29003bebd436'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.add_column('risk_assessments',
                  sa.Column('program_id', sa.Integer(), nullable=False))
    op.alter_column(
        'risk_assessments',
        'title',
        existing_type=mysql.VARCHAR(length=250),
        nullable=False)


def downgrade():
    op.drop_column('risk_assessments', 'program_id')
