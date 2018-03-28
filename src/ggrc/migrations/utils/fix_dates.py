# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Convert date formats in CAV table."""


def _update_date_by_regexp(connection, regexp, new_value):
    """Run an UPDATE cavs SET value = new_value WHERE value REGEXP regexp.

  WARNING: Function arguments are directly passed to the expression, no
  escaping is performed! This function should not be called with arguments from
  an untrusted source!
  """

    request_skeleton = """
      UPDATE custom_attribute_values AS cav JOIN
             custom_attribute_definitions AS cad ON
                 cav.custom_attribute_id = cad.id
      SET cav.attribute_value = {new_value}
      WHERE cad.attribute_type = 'Date' AND
            cav.attribute_value REGEXP '{regexp}'
  """
    connection.execute(
        request_skeleton.format(new_value=new_value, regexp=regexp))


def fix_single_digit_month(connection):
    """Change M/DD/YYYY (M/D/YYYY) into MM/DD/YYYY (MM/D/YYYY) correspondigly."""
    _update_date_by_regexp(
        connection=connection,
        regexp="^[0-9]{1}/[0-9]{1,2}/[0-9]{4}$",
        new_value="CONCAT('0', cav.attribute_value)")


def fix_single_digit_day(connection):
    """Change MM/D/YYYY into MM/DD/YYYY."""
    _update_date_by_regexp(
        connection=connection,
        regexp="^[0-9]{2}/[0-9]{1}/[0-9]{4}$",
        new_value="""CONCAT(SUBSTR(cav.attribute_value, 1, 3),
                                             '0',
                                             SUBSTR(cav.attribute_value, 4, 9))
                         """)


def american_date_to_iso(connection):
    """Change MM/DD/YYYY into YYYY-MM-DD."""
    _update_date_by_regexp(
        connection=connection,
        regexp="^[0-9]{2}/[0-9]{2}/[0-9]{4}$",
        new_value="""CONCAT_WS('-',
                                          SUBSTR(cav.attribute_value, 7, 4),
                                          SUBSTR(cav.attribute_value, 1, 2),
                                          SUBSTR(cav.attribute_value, 4, 2))
                         """)


def strip_trailing_zero_time(connection):
    """Change YYYY-MM-DD 00:00:00 to YYYY-MM-DD."""
    _update_date_by_regexp(
        connection=connection,
        regexp="^[0-9]{4}-[0-9]{2}-[0-9]{2} 00:00:00$",
        new_value="SUBSTR(cav.attribute_value, 1, 10)")


def iso_date_to_american(connection):
    """Change YYYY-MM-DD into MM/DD/YYYY."""
    _update_date_by_regexp(
        connection=connection,
        regexp="^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
        new_value="""CONCAT_WS('/',
                                          SUBSTR(cav.attribute_value, 6, 2),
                                          SUBSTR(cav.attribute_value, 9, 2),
                                          SUBSTR(cav.attribute_value, 1, 4))
                         """)
