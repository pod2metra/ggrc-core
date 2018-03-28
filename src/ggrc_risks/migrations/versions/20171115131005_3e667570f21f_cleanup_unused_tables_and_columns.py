# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Cleanup unused tables and columns

Create Date: 2017-11-15 13:10:05.443564
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from alembic import op

# revision identifiers, used by Alembic.
revision = '3e667570f21f'
down_revision = '564e4bcf092'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.drop_column('risks', 'url')
    op.drop_column('risks', 'reference_url')

    op.drop_column('threats', 'url')
    op.drop_column('threats', 'reference_url')


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.add_column('threats',
                  sa.Column(
                      'reference_url',
                      mysql.VARCHAR(length=250),
                      nullable=True))
    op.add_column('threats',
                  sa.Column('url', mysql.VARCHAR(length=250), nullable=True))

    op.add_column('risks',
                  sa.Column(
                      'reference_url',
                      mysql.VARCHAR(length=250),
                      nullable=True))
    op.add_column('risks',
                  sa.Column('url', mysql.VARCHAR(length=250), nullable=True))
