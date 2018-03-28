# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""redefine risk assessments

Revision ID: 29003bebd436
Revises: 1cf70fb6b6cc
Create Date: 2014-07-16 21:38:34.176935

"""

# revision identifiers, used by Alembic.
revision = '29003bebd436'
down_revision = '1cf70fb6b6cc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # Clear out old tables
    #op.drop_constraint('context_id', 'risk_assessments', type_='foreignkey')
    op.drop_table('risk_assessment_control_mappings')
    op.drop_table('risk_assessment_mappings')
    op.drop_table('risk_assessments')
    op.drop_table('templates')
    op.drop_table('threats')
    op.drop_table('vulnerabilities')

    # Redefine the risk_assessment table
    op.create_table('risk_assessments',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('title', sa.String(length=250), nullable=True),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('notes', sa.Text(), nullable=True),
                    sa.Column('ra_manager_id', sa.Integer(), nullable=True),
                    sa.Column('ra_counsel_id', sa.Integer(), nullable=True),
                    sa.Column('start_date', sa.Date(), nullable=True),
                    sa.Column('end_date', sa.Date(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('modified_by_id', sa.Integer(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('context_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['context_id'],
                        ['contexts.id'],
                    ),
                    sa.ForeignKeyConstraint(
                        ['ra_manager_id'], ['people.id'],
                        name='fk_risk_assessments_manager_person_id'),
                    sa.ForeignKeyConstraint(
                        ['ra_counsel_id'], ['people.id'],
                        name='fk_risk_assessments_counsel_person_id'),
                    sa.PrimaryKeyConstraint('id'))


def downgrade():
    pass
