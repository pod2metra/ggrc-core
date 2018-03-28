# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Initial model.

Revision ID: 113eb68585b7
Revises: None
Create Date: 2014-07-22 22:22:33.632831

"""

# revision identifiers, used by Alembic.
revision = '113eb68585b7'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.create_table('risks', sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('slug', sa.String(length=250), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('modified_by_id', sa.Integer(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('context_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['context_id'],
                        ['contexts.id'],
                    ), sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('slug', name='uq_risks'))
    op.create_index('fk_risks_contexts', 'risks', ['context_id'], unique=False)


def downgrade():
    op.drop_index('fk_risks_contexts', table_name='risks')
    op.drop_table('risks')
