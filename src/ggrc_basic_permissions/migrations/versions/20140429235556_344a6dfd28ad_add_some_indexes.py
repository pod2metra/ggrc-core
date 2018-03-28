# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add some indexes

Revision ID: 344a6dfd28ad
Revises: e1e9986270
Create Date: 2014-04-29 23:55:56.938368

"""

# revision identifiers, used by Alembic.
revision = '344a6dfd28ad'
down_revision = 'e1e9986270'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index(
        'fk_context_implications_contexts',
        'context_implications', ['context_id'],
        unique=False)
    op.create_index('fk_roles_contexts', 'roles', ['context_id'], unique=False)
    op.create_index(
        'fk_user_roles_contexts', 'user_roles', ['context_id'], unique=False)


def downgrade():
    op.drop_index('fk_user_roles_contexts', table_name='user_roles')
    op.drop_index('fk_roles_contexts', table_name='roles')
    op.drop_index(
        'fk_context_implications_contexts', table_name='context_implications')
