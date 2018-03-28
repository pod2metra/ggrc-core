# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Indexes on updated_at

Revision ID: cd51533c624
Revises: 1afd15b0581f
Create Date: 2014-09-12 23:01:22.542186

"""

# revision identifiers, used by Alembic.
revision = 'cd51533c624'
down_revision = '1afd15b0581f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index(
        'ix_risk_assessments_updated_at',
        'risk_assessments', ['updated_at'],
        unique=False)


def downgrade():
    op.drop_index(
        'ix_risk_assessments_updated_at', table_name='risk_assessments')
