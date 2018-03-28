# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add notification types for Assessment state transitions.

Create Date: 2017-02-12 14:39:51.734155
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from datetime import datetime

from alembic import op

from sqlalchemy import Boolean, Date, Integer, String
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = '1e65abd56ccb'
down_revision = '57940269e30'

_NOTIFICATION_TYPES_TABLE = table(
    "notification_types",
    column("name", String),
    column("description", String),
    column("template", String),
    column("advance_notice", Integer),
    column("instant", Boolean),
    column("created_at", Date),
    column("updated_at", Date),
)

_NOW = datetime.utcnow()
_DESCRIPTION_TPL = \
    u"Notify Assessors, Creators and Verifiers that an Assessment {}."

_NOTIFICATION_TYPES = [{
    "name":
    "assessment_completed",
    "description":
    _DESCRIPTION_TPL.format(u"has been completed"),
    "template":
    "assessment_completed",
    "advance_notice":
    0,
    "instant":
    False,
    "created_at":
    _NOW,
    "updated_at":
    _NOW,
}, {
    "name":
    "assessment_ready_for_review",
    "description":
    _DESCRIPTION_TPL.format(u"is ready for review"),
    "template":
    "assessment_ready_for_review",
    "advance_notice":
    0,
    "instant":
    False,
    "created_at":
    _NOW,
    "updated_at":
    _NOW,
}, {
    "name":
    "assessment_verified",
    "description":
    _DESCRIPTION_TPL.format(u"has been verified"),
    "template":
    "assessment_verified",
    "advance_notice":
    0,
    "instant":
    False,
    "created_at":
    _NOW,
    "updated_at":
    _NOW,
}, {
    "name":
    "assessment_reopened",
    "description":
    _DESCRIPTION_TPL.format(u"has been reopened"),
    "template":
    "assessment_reopened",
    "advance_notice":
    0,
    "instant":
    False,
    "created_at":
    _NOW,
    "updated_at":
    _NOW,
}]


def upgrade():
    """Add new notification types for Assessment state transitions.

  The only state transition left out is "Not Started" --> "In Progress",
  because it has no interest to users.
  """
    op.bulk_insert(_NOTIFICATION_TYPES_TABLE, _NOTIFICATION_TYPES)


def downgrade():
    """Remove Assessment state change notification types.

  The only exception is the Assessment declined state transition, i.e. from
  "Ready for Review" to "In Progress".

  Notifications of the deleted notification types get deleted as well.
  """
    notif_type_names = tuple(notif["name"] for notif in _NOTIFICATION_TYPES)

    sql = """
      DELETE n
      FROM notifications AS n
      LEFT JOIN notification_types AS nt ON
          n.notification_type_id = nt.id
      WHERE
          nt.name in {}
  """.format(notif_type_names)

    op.execute(sql)

    sql = _NOTIFICATION_TYPES_TABLE.delete().where(
        _NOTIFICATION_TYPES_TABLE.c.name.in_(notif_type_names))
    op.execute(sql)
