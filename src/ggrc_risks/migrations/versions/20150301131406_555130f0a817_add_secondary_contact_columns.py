# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""add secondary contact columns

Revision ID: 555130f0a817
Revises: 44d5969c897b
Create Date: 2015-03-01 13:14:06.935565

"""

# revision identifiers, used by Alembic.
revision = '555130f0a817'
down_revision = '44d5969c897b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('risks',
                  sa.Column(
                      'secondary_contact_id', sa.Integer(), nullable=True))
    op.create_index(
        'fk_risks_secondary_contact',
        'risks', ['secondary_contact_id'],
        unique=False)
    op.add_column('risk_objects',
                  sa.Column(
                      'secondary_contact_id', sa.Integer(), nullable=True))
    op.create_index(
        'fk_risk_objects_secondary_contact',
        'risk_objects', ['secondary_contact_id'],
        unique=False)
    op.add_column('threat_actors',
                  sa.Column(
                      'secondary_contact_id', sa.Integer(), nullable=True))
    op.create_index(
        'fk_threat_actors_secondary_contact',
        'threat_actors', ['secondary_contact_id'],
        unique=False)


def downgrade():
    op.drop_index('fk_risks_secondary_contact', table_name='risks')
    op.drop_column('risks', 'secondary_contact_id')
    op.drop_index(
        'fk_risk_objects_secondary_contact', table_name='risk_objects')
    op.drop_column('risk_objects', 'secondary_contact_id')
    op.drop_index(
        'fk_threat_actors_secondary_contact', table_name='threat_actors')
    op.drop_column('threat_actors', 'secondary_contact_id')
