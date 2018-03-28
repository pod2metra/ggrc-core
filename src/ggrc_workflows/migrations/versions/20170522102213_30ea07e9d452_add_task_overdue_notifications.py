# -*- coding: utf-8 -*-

# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add task overdue notification type

Create Date: 2017-05-04 09:03:39.661039
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from datetime import datetime, timedelta

from alembic import op

import sqlalchemy as sa
from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = '30ea07e9d452'
down_revision = '1142135ce819'

_NOTIFICATION_TYPES_TABLE = table(
    "notification_types",
    column("name", String),
    column("description", String),
    column("template", String),
    column("advance_notice", Integer),
    column("instant", Boolean),
    column("repeating", Boolean),
    column("created_at", DateTime),
    column("updated_at", DateTime),
)

_NOTIFICATIONS_TABLE = table(
    "notifications",
    column("object_id", Integer),
    column("object_type", String),
    column("notification_type_id", Integer),
    column("send_on", DateTime),
    column("sent_at", DateTime),
    column("custom_message", Text),
    column("force_notifications", Boolean),
    column("created_at", DateTime),
    column("modified_by_id", Integer),
    column("updated_at", DateTime),
    column("context_id", Integer),
    column("repeating", Boolean),
)

_NOW = datetime.utcnow()

_NOTIFICATION_TYPES = [{
    "name":
    "cycle_task_overdue",
    "description": (u"Notify a task assignee that a task is overdue."),
    "template":
    "cycle_task_overdue",
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
    """Add new Workflow Task notification type and a new flag column.

  Also create overdue notification records for all existing active Tasks.
  """
    op.add_column("notifications",
                  sa.Column(
                      "repeating", sa.Boolean(), nullable=False,
                      default=False))

    op.bulk_insert(_NOTIFICATION_TYPES_TABLE, _NOTIFICATION_TYPES)

    # schedule overdue notifications for all currently active tasks
    conn = op.get_bind()

    sql = "SELECT id FROM notification_types WHERE name = 'cycle_task_overdue';"
    overdue_type_id = conn.execute(sql).scalar()  # never None here

    sql = """
      SELECT ct.id AS task_id, ct.end_date
      FROM cycle_task_group_object_tasks AS ct
      LEFT JOIN cycles AS c ON
          ct.cycle_id = c.id
      WHERE
          c.is_current = 1 AND ct.status != "Verified";
  """

    active_tasks = conn.execute(sql).fetchall()
    overdue_notifs = [
        {
            "object_id": task[0],
            "object_type": "CycleTaskGroupObjectTask",
            "notification_type_id": overdue_type_id,
            "send_on": (task[1] + timedelta(1)).isoformat(),
            "force_notifications":
            0,  # not applicable to overdue notifications
            "created_at": _NOW,
            "updated_at": _NOW,
            "repeating": 1,
        } for task in active_tasks
    ]

    op.bulk_insert(_NOTIFICATIONS_TABLE, overdue_notifs)


def downgrade():
    """Remove Task overdue notification type and the `repeating` column.

  All notifications of the deleted notification type get deleted as well.
  """
    sql = """
      DELETE n
      FROM notifications AS n
      LEFT JOIN notification_types AS nt ON
          n.notification_type_id = nt.id
      WHERE
          nt.name = "cycle_task_overdue"
  """

    op.execute(sql)

    sql = _NOTIFICATION_TYPES_TABLE.delete().where(
        _NOTIFICATION_TYPES_TABLE.c.name == "cycle_task_overdue")
    op.execute(sql)

    op.drop_column("notifications", "repeating")
