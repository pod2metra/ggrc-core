# -*- coding: utf-8 -*-

# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add Assessment started state transition

Create Date: 2017-06-08 13:03:00.386896
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from datetime import datetime

from alembic import op

from sqlalchemy import Boolean, Date, Integer, String
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = "56108297b924"
down_revision = "4936d6e2f8dd"

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

_NOTIFICATION_TYPES = [{
    "name":
    "assessment_started",
    "description":
    (u"Notify the people assigned to an Assessment that the latter has "
     u"moved to In Progress."),
    "template":
    "assessment_started",
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
    """Add new Assessment state change notification - "assessment started"."""
    op.bulk_insert(_NOTIFICATION_TYPES_TABLE, _NOTIFICATION_TYPES)


def downgrade():
    """Remove "assessment started" notification type.

  Notifications of the removed notification type themselves get removed, too.
  """
    sql = """
      DELETE n
      FROM notifications AS n
      LEFT JOIN notification_types AS nt ON
          n.notification_type_id = nt.id
      WHERE
          nt.name = "assessment_started"
  """

    op.execute(sql)

    sql = _NOTIFICATION_TYPES_TABLE.delete().where(
        _NOTIFICATION_TYPES_TABLE.c.name == "assessment_started")
    op.execute(sql)
