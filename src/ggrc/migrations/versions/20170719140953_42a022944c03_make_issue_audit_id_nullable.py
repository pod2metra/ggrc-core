# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Make issue.audit_id nullable

Create Date: 2017-07-19 14:09:53.303518
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '42a022944c03'
down_revision = '434683ceff87'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.alter_column(
        'issues',
        'audit_id',
        existing_type=mysql.INTEGER(display_width=11),
        nullable=True)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    connection = op.get_bind()
    lone_issues = connection.execute("""
      SELECT id FROM issues WHERE audit_id IS NULL
  """).fetchall()

    if lone_issues:
        raise RuntimeError(
            "Some Issues are not mapped to any Audit. It was not "
            "allowed in previous versions. Please map these Issues "
            "to Audits to allow downgrade: {}".format(", ".join(
                str(issue[0]) for issue in lone_issues)))

    op.drop_constraint("fk_issues_audits", "issues", type_="foreignkey")
    op.alter_column(
        'issues',
        'audit_id',
        existing_type=mysql.INTEGER(display_width=11),
        nullable=False)
    op.create_foreign_key("fk_issues_audits", "issues", "audits", ["audit_id"],
                          ["id"])
