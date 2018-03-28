# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Unify CA date format

Create Date: 2016-10-20 08:25:01.140510
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op
from sqlalchemy.sql import text

from ggrc.migrations.utils import fix_dates

# revision identifiers, used by Alembic.
revision = '53206b20c12b'
down_revision = 'bb6fe8e14bb'


def _strip_whitespace_around_dates(connection):
    """Fix possibly existing dates prefixed with spaces in the DB."""

    dates = connection.execute("""
      SELECT cavs.id as id, attribute_value as value
      FROM custom_attribute_values AS cavs JOIN
           custom_attribute_definitions as cads ON
               cads.id = cavs.custom_attribute_id
      WHERE attribute_type = 'Date'
  """)

    for date in dates:
        if date.value is None:
            new_value = None
        else:
            new_value = date.value.strip()
        if date.value != new_value:
            connection.execute(
                text("""
          UPDATE custom_attribute_values SET
              attribute_value = :val
          WHERE id = :id
      """),
                val=new_value,
                id=date.id)


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    connection = op.get_bind()

    _strip_whitespace_around_dates(connection)

    fix_dates.fix_single_digit_month(connection)
    fix_dates.fix_single_digit_day(connection)
    fix_dates.american_date_to_iso(connection)

    fix_dates.strip_trailing_zero_time(connection)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    connection = op.get_bind()

    fix_dates.iso_date_to_american(connection)
