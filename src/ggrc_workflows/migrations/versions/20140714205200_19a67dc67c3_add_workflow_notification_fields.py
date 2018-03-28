# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add workflow notification fields

Revision ID: 19a67dc67c3
Revises: 51ec129d9dde
Create Date: 2014-07-14 20:52:00.013439

"""

# revision identifiers, used by Alembic.
revision = '19a67dc67c3'
down_revision = '51ec129d9dde'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('workflows',
                  sa.Column(
                      'notify_custom_message',
                      sa.String(length=250),
                      nullable=True))
    op.add_column('workflows',
                  sa.Column('notify_on_change', sa.Boolean(), nullable=False))


def downgrade():
    op.drop_column('workflows', 'notify_on_change')
    op.drop_column('workflows', 'notify_custom_message')
