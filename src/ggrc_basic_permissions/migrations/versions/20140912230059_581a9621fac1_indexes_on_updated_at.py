# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Indexes on updated_at

Revision ID: 581a9621fac1
Revises: 1d1573d5812f
Create Date: 2014-09-12 23:00:59.734064

"""

# revision identifiers, used by Alembic.
revision = '581a9621fac1'
down_revision = '1d1573d5812f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index(
        'ix_context_implications_updated_at',
        'context_implications', ['updated_at'],
        unique=False)
    op.create_index(
        'ix_contexts_updated_at', 'contexts', ['updated_at'], unique=False)
    op.create_index(
        'ix_roles_updated_at', 'roles', ['updated_at'], unique=False)
    op.create_index(
        'ix_user_roles_updated_at', 'user_roles', ['updated_at'], unique=False)


def downgrade():
    op.drop_index('ix_user_roles_updated_at', table_name='user_roles')
    op.drop_index('ix_roles_updated_at', table_name='roles')
    op.drop_index('ix_contexts_updated_at', table_name='contexts')
    op.drop_index(
        'ix_context_implications_updated_at',
        table_name='context_implications')
