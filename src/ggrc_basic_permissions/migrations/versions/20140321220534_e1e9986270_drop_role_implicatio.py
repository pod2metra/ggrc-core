# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Drop role_implications table

Revision ID: e1e9986270
Revises: 476e9e882141
Create Date: 2014-03-21 22:05:34.067126

"""

# revision identifiers, used by Alembic.
revision = 'e1e9986270'
down_revision = '476e9e882141'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.drop_table(u'role_implications')


def downgrade():
    op.create_table(
        'role_implications',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('source_context_id', sa.Integer(), nullable=True),
        sa.Column('context_id', sa.Integer(), nullable=True),  #target
        sa.Column('source_role_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),  #target
        sa.Column('modified_by_id', sa.Integer(), nullable=False),
        sa.Column(
            'created_at', sa.DateTime(), default=sa.text('current_timestamp')),
        sa.Column(
            'updated_at',
            sa.DateTime(),
            default=sa.text('current_timestamp'),
            onupdate=sa.text('current_timestamp'),
        ),
        sa.ForeignKeyConstraint([
            'source_context_id',
        ], [
            'contexts.id',
        ]),
        sa.ForeignKeyConstraint([
            'context_id',
        ], [
            'contexts.id',
        ]),
        sa.ForeignKeyConstraint([
            'source_role_id',
        ], [
            'roles.id',
        ]),
        sa.ForeignKeyConstraint([
            'role_id',
        ], [
            'roles.id',
        ]),
    )
