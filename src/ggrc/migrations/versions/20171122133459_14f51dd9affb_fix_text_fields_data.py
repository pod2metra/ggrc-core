# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Set all 'text' fields NOT NULLABLE to all tables across the schema

Create Date: 2017-11-22 13:34:59.264965
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa
from sqlalchemy.sql import text
from alembic import op

# revision identifiers, used by Alembic.
revision = '14f51dd9affb'
down_revision = '41f1fe4700d9'

IGNORE_TABLES = {
    "custom_attribute_definitions",
}


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    connection = op.get_bind()
    db_name = connection.engine.url.database
    results = connection.execute(
        text("""
      SELECT TABLE_NAME, COLUMN_NAME FROM information_schema.columns
      WHERE table_schema = :db_name
      AND data_type = 'text'
      AND is_nullable = 'YES';
      """),
        db_name=db_name)
    query = "UPDATE {table_name} SET {col_name}='' WHERE {col_name} IS NULL;"
    for table_name, col_name in results:
        if table_name in IGNORE_TABLES:
            continue
        print "Replacing null values in: {} - {}".format(table_name, col_name)
        connection.execute(
            query.format(table_name=table_name, col_name=col_name))
        print "Setting filed to non-nullable: {} - {}".format(
            table_name, col_name)
        op.alter_column(
            table_name, col_name, nullable=False, existing_type=sa.Text())


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    pass
