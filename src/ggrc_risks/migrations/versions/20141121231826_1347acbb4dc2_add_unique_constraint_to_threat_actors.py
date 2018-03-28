# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add unique constraint to threat actors

Revision ID: 1347acbb4dc2
Revises: 5ada65dc60b3
Create Date: 2014-11-21 23:18:26.689048

"""

# revision identifiers, used by Alembic.
revision = '1347acbb4dc2'
down_revision = '5ada65dc60b3'

from alembic import op


def upgrade():
    op.create_unique_constraint('uq_t_actors', 'threat_actors', ['title'])


def downgrade():
    op.drop_constraint('uq_t_actors', 'threat_actors', 'unique')
