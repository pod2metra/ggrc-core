# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add assignable notification types

Create Date: 2016-03-04 12:45:23.024224
"""

# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa
from sqlalchemy.sql import column
from sqlalchemy.sql import table
from alembic import op

# revision identifiers, used by Alembic.
revision = '50c374901d42'
down_revision = '4fd36860d196'

NOTIFICATION_TYPES = table(
    'notification_types',
    column('id', sa.Integer),
    column('name', sa.String),
    column('description', sa.Text),
    column('template', sa.String),
    column('instant', sa.Boolean),
    column('advance_notice', sa.Integer),
    column('advance_notice_end', sa.Integer),
    column('created_at', sa.DateTime),
    column('modified_by_id', sa.Integer),
    column('updated_at', sa.DateTime),
    column('context_id', sa.Integer),
)

NOTIFICATIONS = [{
    "name":
    "request_open",
    "description": ("Notify all assignees Requesters Assignees and "
                    "Verifiers that a new request has been created."),
    "template":
    "request_open",
    "advance_notice":
    0,
    "instant":
    False,
}, {
    "name":
    "request_declined",
    "description":
    "Notify Requester that a request has been declined.",
    "template":
    "request_declined",
    "advance_notice":
    0,
    "instant":
    False,
}, {
    "name":
    "request_manual",
    "description":
    "Send a manual notification to the Requester.",
    "template":
    "request_manual",
    "advance_notice":
    0,
    "instant":
    False,
}, {
    "name":
    "assessment_open",
    "description": ("Send an open assessment notification to Assessors, "
                    "Assignees and Verifiers."),
    "template":
    "assessment_open",
    "advance_notice":
    0,
    "instant":
    False,
}, {
    "name":
    "assessment_declined",
    "description":
    "Notify Assessor that an assessment was declined.",
    "template":
    "assessment_declined",
    "advance_notice":
    0,
    "instant":
    False,
}, {
    "name":
    "assessment_manual",
    "description":
    "Send a manual notification to the Requester.",
    "template":
    "assessment_manual",
    "advance_notice":
    0,
    "instant":
    False,
}]


def upgrade():
    """Add notification type entries for requests and assessments."""
    op.bulk_insert(NOTIFICATION_TYPES, NOTIFICATIONS)


def downgrade():
    """Remove notification type entries for requests and assessments."""
    notification_names = tuple([notif["name"] for notif in NOTIFICATIONS])
    op.execute("""
      DELETE n
      FROM notifications AS n
      LEFT JOIN notification_types AS nt
        ON n.notification_type_id = nt.id
      WHERE nt.name IN {}
      """.format(str(notification_names)))
    op.execute(NOTIFICATION_TYPES.delete().where(
        NOTIFICATION_TYPES.c.name.in_(notification_names)))
