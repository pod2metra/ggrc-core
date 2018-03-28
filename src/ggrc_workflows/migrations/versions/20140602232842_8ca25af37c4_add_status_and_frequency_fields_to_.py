# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add status and frequency fields to workflow

Revision ID: 8ca25af37c4
Revises: 1d33919af441
Create Date: 2014-06-02 23:28:42.711269

"""

# revision identifiers, used by Alembic.
revision = '8ca25af37c4'
down_revision = '1d33919af441'

from alembic import op
import sqlalchemy as sa


def upgrade():
    #op.add_column(u'workflows', sa.Column(u'status', sa.String(length=250), nullable=True))
    op.add_column(u'workflows',
                  sa.Column(
                      u'frequency', sa.String(length=250), nullable=True))


def downgrade():
    #op.drop_column(u'workflows', u'status')
    op.drop_column(u'workflows', u'frequency')
