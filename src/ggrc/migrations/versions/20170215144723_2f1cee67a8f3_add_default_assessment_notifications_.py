# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add default Assessment notifications settings.

Create Date: 2017-02-15 14:47:23.772467
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "2f1cee67a8f3"
down_revision = "1e65abd56ccb"


def upgrade():
    """Enable sending Assessment comment notifications by default.

  The notifications should (by default) be sent to all people roles assigned
  to a particular Assessment.
  """
    sql = """
    UPDATE assessments
    SET send_by_default = 1
    WHERE send_by_default IS NULL
  """
    op.execute(sql)

    sql = """
    UPDATE assessments
    SET recipients = "Assessor,Creator,Verifier"
    WHERE recipients IS NULL
  """
    op.execute(sql)

    op.alter_column(
        "assessments",
        "send_by_default",
        server_default=u"1",
        existing_type=sa.Integer(),
        existing_nullable=True)

    op.alter_column(
        "assessments",
        "recipients",
        server_default=u"Assessor,Creator,Verifier",
        existing_type=mysql.VARCHAR(length=250),
        existing_nullable=True)


def downgrade():
    """Remove default settings for Assessment comment notifications."""
    op.alter_column(
        "assessments",
        "send_by_default",
        server_default=None,
        existing_type=sa.Integer(),
        existing_nullable=True)

    op.alter_column(
        "assessments",
        "recipients",
        server_default=None,
        existing_type=mysql.VARCHAR(length=250),
        existing_nullable=True)
