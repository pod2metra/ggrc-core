# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Rename Effective Date to Due Date for Assessment

Create Date: 2017-09-29 15:05:01.641261
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name
from alembic import op

revision = '5299857cfde0'
down_revision = 'a153c7b1b41'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.execute("""
      UPDATE assessments asmt
      JOIN custom_attribute_values cav ON cav.attributable_id = asmt.id
      JOIN custom_attribute_definitions cad ON cad.id = cav.custom_attribute_id
      SET asmt.start_date = CASE
          WHEN cav.attribute_value = '' THEN NULL
          ELSE cav.attribute_value
        END
      WHERE cad.title = 'Due Date' AND
          cad.definition_type = 'assessment' AND
          cad.attribute_type = 'Date';
  """)
    op.execute("""
      # CAVs will be removed cascade
      DELETE FROM custom_attribute_definitions
      WHERE title = 'Due Date' AND
          definition_type = 'assessment';
  """)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.execute("""
      INSERT INTO custom_attribute_definitions(
        created_at, updated_at, title, definition_type,
        attribute_type, mandatory
      )
      VALUES(now(), now(), 'Due Date', 'assessment', 'Date', 0)
  """)
    op.execute("""
      INSERT INTO custom_attribute_values(
        created_at, updated_at, custom_attribute_id, attributable_id,
        attributable_type, attribute_value
      )
      SELECT now(), now(), cad.id, a.id, "Assessment", start_date
      FROM assessments a, custom_attribute_definitions cad
      WHERE cad.title = 'Due Date' AND
          cad.definition_type = 'assessment' AND
          cad.attribute_type = 'Date' AND
          a.start_date IS NOT NULL
      GROUP BY cad.id, a.id, start_date;  -- Process case when CADs duplicated
  """)
    op.execute("""
      UPDATE assessments
      SET start_date = NULL;
  """)
