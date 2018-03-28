# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Remove contact columns

Create Date: 2017-10-20 10:59:22.859589
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision = '564e4bcf092'
down_revision = '1be0dd01f559'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.drop_index(
        'fk_risk_objects_secondary_contact', table_name='risk_objects')
    op.drop_index('fk_risks_secondary_contact', table_name='risks')
    op.drop_index('fk_threat_actors_secondary_contact', table_name='threats')

    op.drop_column('risk_objects', 'secondary_contact_id')
    op.drop_column('risks', 'secondary_contact_id')
    op.drop_column('risks', 'contact_id')
    op.drop_column('threats', 'secondary_contact_id')
    op.drop_column('threats', 'contact_id')


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.add_column('threats',
                  sa.Column(
                      'contact_id',
                      mysql.INTEGER(display_width=11),
                      autoincrement=False,
                      nullable=True))
    op.add_column('threats',
                  sa.Column(
                      'secondary_contact_id',
                      mysql.INTEGER(display_width=11),
                      autoincrement=False,
                      nullable=True))
    op.add_column('risks',
                  sa.Column(
                      'contact_id',
                      mysql.INTEGER(display_width=11),
                      autoincrement=False,
                      nullable=True))
    op.add_column('risks',
                  sa.Column(
                      'secondary_contact_id',
                      mysql.INTEGER(display_width=11),
                      autoincrement=False,
                      nullable=True))
    op.add_column('risk_objects',
                  sa.Column(
                      'secondary_contact_id',
                      mysql.INTEGER(display_width=11),
                      autoincrement=False,
                      nullable=True))
    op.create_index(
        'fk_threat_actors_secondary_contact',
        'threats', ['secondary_contact_id'],
        unique=False)
    op.create_index(
        'fk_risks_secondary_contact',
        'risks', ['secondary_contact_id'],
        unique=False)
    op.create_index(
        'fk_risk_objects_secondary_contact',
        'risk_objects', ['secondary_contact_id'],
        unique=False)
