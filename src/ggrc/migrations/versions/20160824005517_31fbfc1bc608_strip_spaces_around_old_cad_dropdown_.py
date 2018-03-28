# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Strip spaces around old CAD dropdown parameters

Create Date: 2016-08-24 00:55:17.547549
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = "31fbfc1bc608"
down_revision = "24296c08e80"


def _strip_and_zip_options_and_bitmaps(cad):
    """Get dropdown info from cad, strip options and zip them with bitmaps.

  Args:
    cad: named tuple like (cad.id, cad.multi_choice_options,
                           cad.multi_choice_mandatory).

  Returns:
    [(dropdown_option, mandatory_bitmap), ...] for every option in dropdown cad
  """
    options = [opt.strip() for opt in cad.multi_choice_options.split(",")]
    if cad.multi_choice_mandatory is None:
        bitmaps = [None] * len(options)
    else:
        bitmaps = [
            bitmap.strip() for bitmap in cad.multi_choice_mandatory.split(",")
        ]
    return zip(options, bitmaps)


def _deduplicate_and_remove_empty_options(zipped):
    """Remove option-bitmap pairs where option is duplicate or empty.

  Args:
    zipped: list of tuples [(option, bitmap), ...].

  Returns:
    `zipped` without such elements where `option` is duplicate in the list or
    is empty.
  """
    stored_options = set()
    zipped_unique = []
    for (option, bitmap) in zipped:
        # remove empty options and duplicate options at once
        if option and option not in stored_options:
            zipped_unique.append((option, bitmap))
            stored_options.add(option)
    return zipped_unique


def _unzip_and_make_csv(zipped):
    """Unzip options and bitmaps and make comma-separated strings from them.

  Args:
    zipped: list of tuples [(options, bitmap), ...].

  Returns:
    (options, bitmaps) - a tuple of strings or a tuple of string and None.

  bitmaps is None if every bitmap in zipped is None (meaning no bitmap was
  stored in the db) or zipped has zero length.
  """
    options_new, bitmaps_new = zip(*zipped) if zipped else ([], [])

    options_new = ",".join(options_new)
    if not bitmaps_new or not any(bitmaps_new):
        # no bitmaps were defined
        bitmaps_new = None
    else:
        bitmaps_new = ",".join(bitmaps_new)
    return options_new, bitmaps_new


def upgrade():
    """Upgrade database schema and/or data, creating a new revision.

  1. Strip every dropdown option of leading and trailing whitespace.
  2. Remove duplicate dropdown options in every CAD.
  3. Remove empty dropdown options in every CAD (leave one empty dropdown
  option if there are no non-empty options).
  4. Strip every value of CAV for Dropdown-type CAD of leading and trailing
  whitespace.
  """
    connection = op.get_bind()

    cads = connection.execute("""
      SELECT id, multi_choice_options, multi_choice_mandatory
      FROM custom_attribute_definitions
      WHERE attribute_type = 'Dropdown' AND
            multi_choice_options IS NOT NULL
  """).fetchall()
    for cad in cads:
        zipped = _strip_and_zip_options_and_bitmaps(cad)
        zipped_unique = _deduplicate_and_remove_empty_options(zipped)
        options_new, bitmaps_new = _unzip_and_make_csv(zipped_unique)

        if (cad.multi_choice_options != options_new
                or cad.multi_choice_mandatory != bitmaps_new):
            connection.execute(
                text("""
          UPDATE custom_attribute_definitions SET
              multi_choice_options = :mco,
              multi_choice_mandatory = :mcm
          WHERE id = :id
      """),
                mco=options_new,
                mcm=bitmaps_new,
                id=cad.id)

    cavs = connection.execute("""
      SELECT cavs.id as id, attribute_value
      FROM custom_attribute_values as cavs JOIN
           custom_attribute_definitions as cads ON
               cads.id = cavs.custom_attribute_id
      WHERE cads.attribute_type = 'Dropdown'
  """)
    for cav in cavs:
        if cav.attribute_value is None:
            new_attribute_value = None
        else:
            new_attribute_value = cav.attribute_value.strip()

        if cav.attribute_value != new_attribute_value:
            connection.execute(
                text("""
          UPDATE custom_attribute_values SET
              attribute_value = :av
          WHERE id = :id
      """),
                av=new_attribute_value,
                id=cav.id)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    # it is not possible to add the removed spaces and items back to the values
    pass
