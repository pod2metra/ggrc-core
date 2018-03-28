# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add Assessment updated notification type

Create Date: 2017-02-07 13:42:38.921370
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from datetime import datetime

from alembic import op

# revision identifiers, used by Alembic.
revision = '562ec606ff7c'
down_revision = '6e9a3ed063d2'


def upgrade():
    """Add new notification type: Assessment updated."""
    description = ("Send an Assessment updated notification to "
                   "Assessors, Creators and Verifiers.")

    now = datetime.utcnow().strftime("%Y-%m-%d %H-%M-%S")

    sql = """
    INSERT INTO notification_types (
        name,
        description,
        template,
        advance_notice,
        instant,
        created_at,
        updated_at
    )
    VALUES (
        "assessment_updated",
        "{description}",
        "assessment_updated",
        0,
        FALSE,
        '{now}',
        '{now}'
    )
  """.format(
        description=description, now=now)

    op.execute(sql)


def downgrade():
    """Remove the "Assessment updated" notification type.

  Also delete all notifications of that type.
  """
    sql = """
    DELETE n
    FROM notifications AS n
    LEFT JOIN notification_types AS nt ON
        n.notification_type_id = nt.id
    WHERE
        nt.name = "assessment_updated"
  """
    op.execute(sql)

    sql = """
    DELETE
    FROM notification_types
    WHERE name = "assessment_updated"
  """
    op.execute(sql)
