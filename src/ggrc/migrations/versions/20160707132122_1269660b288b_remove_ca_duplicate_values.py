# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
remove ca duplicate values

Create Date: 2016-07-07 13:21:22.732299
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = '1269660b288b'
down_revision = '3a0c977a9cb8'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""

    # Remove duplicate lines and include only the newest ones.
    # This relies on the newest lines having the biggest id.
    connection = op.get_bind()
    good_rows = connection.execute("""
      SELECT MAX(id) AS id
      FROM custom_attribute_values
      GROUP BY custom_attribute_id, attributable_id
  """).fetchall()
    all_rows = connection.execute(
        "SELECT id FROM custom_attribute_values").fetchall()
    good_ids = set(row[0] for row in good_rows)
    all_ids = set(row[0] for row in all_rows)

    bad_ids = [str(i) for i in all_ids.difference(good_ids)]

    if bad_ids:
        op.execute("""
        DELETE FROM custom_attribute_values
        WHERE id IN ({bad_ids})
        """.format(bad_ids=",".join(bad_ids)))

    # The unique constraint does not include the attributable_type since that is
    # already specified in the custom attribute definition (custom_attribute_id)
    # and we should avoid adding string values to indexes.
    op.create_unique_constraint("uq_custom_attribute_value",
                                "custom_attribute_values",
                                ["custom_attribute_id", "attributable_id"])


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_constraint(
        "uq_custom_attribute_value", "custom_attribute_values", type_="unique")
