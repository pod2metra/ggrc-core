# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add AssessmentTemplate

Revision ID: 1894405f14ef
Revises: 1e2abee7566c
Create Date: 2016-02-25 11:49:25.128231

"""

# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '1894405f14ef'
down_revision = '1e2abee7566c'


def upgrade():
    """Upgrade database schema to a new revision."""
    op.create_table('assessment_templates',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column(
                        'template_object_type',
                        sa.String(length=250),
                        nullable=True),
                    sa.Column(
                        'test_plan_procedure', sa.Boolean(), nullable=False),
                    sa.Column(
                        'procedure_description', sa.Text(), nullable=True),
                    sa.Column('default_people', sa.Text(), nullable=False),
                    sa.Column('created_at', sa.DateTime()),
                    sa.Column('modified_by_id', sa.Integer()),
                    sa.Column('updated_at', sa.DateTime()),
                    sa.Column('context_id', sa.Integer(),
                              sa.ForeignKey('contexts.id')),
                    sa.PrimaryKeyConstraint('id'))


def downgrade():
    """Downgrade the database schema to the previous revision."""
    op.drop_table('assessment_templates')
