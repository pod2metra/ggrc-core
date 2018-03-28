# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add some more indexes

Revision ID: 5560713e91b2
Revises: 344a6dfd28ad
Create Date: 2014-04-30 06:45:08.197351

"""

# revision identifiers, used by Alembic.
revision = '5560713e91b2'
down_revision = '344a6dfd28ad'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index(
        'ix_user_roles_person', 'user_roles', ['person_id'], unique=False)


def downgrade():
    op.drop_index('ix_user_roles_person', table_name='user_roles')
