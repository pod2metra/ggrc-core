# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
empty message

Create Date: 2017-10-24 10:22:41.063004
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op


# revision identifiers, used by Alembic.
revision = '65c48993828'
down_revision = '1acc17635676'


INSERT_SQL = """INSERT INTO labels (name, object_type, updated_at, created_at)
    VALUES
    ("Needs Discussion", "Assessment", now(), now()),
    ("Needs Rework", "Assessment", now(), now()),
    ("Followup", "Assessment", now(), now()),
    ("Auditor pulls evidence", "Assessment", now(), now());"""

DELETE_SQL = """DELETE FROM labels
WHERE object_type = "Assessment" and
      name IN ("Needs Discussion", "Needs Rework",
               "Followup", "Auditor pulls evidence");
"""


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  op.execute(INSERT_SQL)


def downgrade():
  """Downgrade database schema and/or data back to the previous revision."""
  op.execute(DELETE_SQL)
