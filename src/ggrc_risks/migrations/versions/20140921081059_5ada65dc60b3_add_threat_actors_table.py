# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add threat_actors table

Revision ID: 5ada65dc60b3
Revises: 5aa58c3b1867
Create Date: 2014-09-21 08:10:59.441988

"""

# revision identifiers, used by Alembic.
revision = '5ada65dc60b3'
down_revision = '5aa58c3b1867'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('threat_actors',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('modified_by_id', sa.Integer(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('url', sa.String(length=250), nullable=True),
                    sa.Column('start_date', sa.Date(), nullable=True),
                    sa.Column('end_date', sa.Date(), nullable=True),
                    sa.Column('slug', sa.String(length=250), nullable=False),
                    sa.Column('title', sa.String(length=250), nullable=False),
                    sa.Column('context_id', sa.Integer(), nullable=True),
                    sa.Column('contact_id', sa.Integer(), nullable=True),
                    sa.Column('notes', sa.Text(), nullable=True),
                    sa.Column('status', sa.String(length=250), nullable=True),
                    sa.Column(
                        'reference_url', sa.String(length=250), nullable=True),
                    sa.PrimaryKeyConstraint('id'))


def downgrade():
    op.drop_table('threat_actors')
