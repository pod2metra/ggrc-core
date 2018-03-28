# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Delete responses table and any other references to responses

Create Date: 2016-04-21 14:19:28.527745
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '1257140cbce5'
down_revision = '5599d1769f25'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.drop_constraint('meetings_ibfk_3', 'meetings', type_='foreignkey')
    op.drop_column('meetings', 'response_id')
    op.drop_table('responses')


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.create_table(
        'responses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('request_id', sa.Integer(), nullable=False),
        sa.Column(
            'response_type',
            sa.Enum(u'documentation', u'interview', u'population sample'),
            nullable=False),
        sa.Column('status', sa.String(length=250), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=250), nullable=False),
        sa.Column('slug', sa.String(length=250), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('modified_by_id', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('context_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('url', sa.String(length=250), nullable=True),
        sa.Column('population_count', sa.Integer(), nullable=True),
        sa.Column('sample_count', sa.Integer(), nullable=True),
        sa.Column('population_worksheet_id', sa.Integer(), nullable=True),
        sa.Column('sample_worksheet_id', sa.Integer(), nullable=True),
        sa.Column('sample_evidence_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('reference_url', sa.String(length=250), nullable=True),
        sa.Column('secondary_contact_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['context_id'], ['contexts.id'], name='responses_ibfk_1'),
        sa.ForeignKeyConstraint(
            ['request_id'], ['requests.id'], name='responses_ibfk_3'),
        sa.ForeignKeyConstraint(
            ['population_worksheet_id'], ['documents.id'],
            name='population_worksheet_document'),
        sa.ForeignKeyConstraint(
            ['sample_worksheet_id'], ['documents.id'],
            name='sample_worksheet_document'),
        sa.ForeignKeyConstraint(
            ['sample_evidence_id'], ['documents.id'],
            name='sample_evidence_document'),
        sa.Index('request_id', 'request_id'),
        sa.Index('fk_responses_contexts', 'context_id'),
        sa.Index('fk_responses_contact', 'contact_id'),
        sa.Index('ix_responses_updated_at', 'updated_at'),
        sa.Index('fk_responses_secondary_contact', 'secondary_contact_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.execute('TRUNCATE TABLE meetings')
    op.add_column('meetings',
                  sa.Column('response_id', sa.Integer(), nullable=False))
    op.create_foreign_key('meetings_ibfk_3', 'meetings', 'responses',
                          ['response_id'], ['id'])
