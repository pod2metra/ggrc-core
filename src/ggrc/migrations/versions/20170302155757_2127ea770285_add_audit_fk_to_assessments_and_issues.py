# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add audit FK to assessments and issues

Create Date: 2017-03-02 15:57:57.006126
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '2127ea770285'
down_revision = '1a5ec1ed04af'


def _check_invalid_state(table_name):
    """Check if database is in invalid state for migrating a given table."""
    connection = op.get_bind()
    results = connection.execute("""
      SELECT t.id
      FROM {table_name} AS t
      LEFT JOIN contexts AS c ON
          c.id = t.context_id AND
          c.related_object_type = "Audit"
      LEFT JOIN audits AS au ON
          c.related_object_id = au.id
      WHERE
        au.id IS NULL
  """.format(table_name=table_name, )).fetchall()

    if results:
        ids = [str(line[0]) for line in results]

        print("There are invalid {table_name} in the database."
              "\nYou can remove them by running:\n\n"
              "DELETE FROM {table_name} WHERE id IN ({ids})\n\n".format(
                  table_name=table_name,
                  ids=", ".join(ids),
              ))

        return True
    return False


def upgrade_table(table_name):
    """Add audit foreign key to a table."""

    op.add_column(table_name, sa.Column(
        "audit_id", sa.Integer(), nullable=True))
    op.execute("""
      UPDATE {table_name} AS t
      JOIN contexts AS c ON
          c.id = t.context_id AND
          c.related_object_type = "Audit"
      JOIN audits AS au ON
          c.related_object_id = au.id
      SET
        t.audit_id = au.id
  """.format(table_name=table_name, ))

    op.alter_column(
        table_name, "audit_id", existing_type=sa.Integer(), nullable=False)

    op.create_foreign_key(
        "fk_{}_audits".format(table_name),
        table_name,
        "audits", ["audit_id"], ["id"],
        ondelete="RESTRICT")


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""

    bad_assessments = _check_invalid_state("assessments")
    bad_issues = _check_invalid_state("issues")
    if bad_assessments or bad_issues:
        raise Exception("Invalid database state for a given migration")

    upgrade_table("assessments")
    upgrade_table("issues")


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_constraint(
        "fk_assessments_audits", "assessments", type_="foreignkey")
    op.drop_constraint("fk_issues_audits", "issues", type_="foreignkey")
    op.drop_column("assessments", "audit_id")
    op.drop_column("issues", "audit_id")
