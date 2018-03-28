# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Rename Assessment state from 'Ready for Review' to 'In Review'

Create Date: 2017-08-17 14:01:44.821309
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name
from alembic import op

from sqlalchemy import text

revision = '51d5958779f1'
down_revision = '191c7cc1fed8'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    connection = op.get_bind()
    updating_ids = connection.execute("""
        SELECT id
        FROM assessments
        WHERE status = 'Ready for Review';
    """).fetchall()
    # Convert ids in tuples to integers
    updating_ids = [id_[0] for id_ in updating_ids]

    op.execute("""
      ALTER TABLE assessments CHANGE status status
      ENUM("Not Started", "In Progress", "In Review", "Verified",
      "Completed") NOT NULL;
  """)

    if updating_ids:
        connection.execute(
            text("""
        UPDATE assessments
        SET status="In Review"
        WHERE id IN :ids;
    """),
            ids=updating_ids)

    op.execute("""
      UPDATE fulltext_record_properties
      SET content="In Review"
      WHERE content="Ready for Review";
  """)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    connection = op.get_bind()
    updating_ids = connection.execute("""
      SELECT id
      FROM assessments
      WHERE status = 'In Review';
  """).fetchall()
    # Convert ids in tuples to integers
    updating_ids = [id_[0] for id_ in updating_ids]

    op.execute("""
      ALTER TABLE assessments CHANGE status status
      ENUM("Not Started", "In Progress", "Ready for Review", "Verified",
      "Completed") NOT NULL;
  """)

    if updating_ids:
        connection.execute(
            text("""
        UPDATE assessments
        SET status="Ready for Review"
        WHERE id IN :ids;
    """),
            ids=updating_ids)

    op.execute("""
      UPDATE fulltext_record_properties
      SET content="Ready for Review"
      WHERE content="In Review";
  """)
