# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add 'subproperty' column into 'fulltext_record_properties' table to make
search by property subtype bypossible.

For example:
We have two subtypes of the property Person:
- name
- email

Create Date: 2017-02-14 10:17:00.155675
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision = '5335453abae'
down_revision = '4c5be77c5da3'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.add_column('fulltext_record_properties',
                  sa.Column(
                      'subproperty',
                      mysql.VARCHAR(length=64),
                      nullable=False,
                      server_default=''))
    op.execute("""
      ALTER TABLE fulltext_record_properties
      DROP PRIMARY KEY,
      ADD PRIMARY KEY (`key`, `type`, property, subproperty);
  """)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.execute("""
      TRUNCATE TABLE fulltext_record_properties;
  """)
    op.drop_column('fulltext_record_properties', 'subproperty')
