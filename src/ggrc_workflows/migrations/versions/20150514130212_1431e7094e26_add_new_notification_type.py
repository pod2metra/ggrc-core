# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""add new notification type

Revision ID: 1431e7094e26
Revises: 2b89912f95f1
Create Date: 2015-05-14 13:02:12.165612

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = '1431e7094e26'
down_revision = '2b89912f95f1'


def upgrade():
    notification_types_table = table(
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

    notification_types = [
        # cycle created notifictions
        {
            "name":
            "cycle_start_failed",
            "description": ("Notify workflow owners that a cycle has failed to"
                            "start for a recurring workflow"),
            "template":
            "cycle_start_failed",
            "advance_notice":
            0,
            "instant":
            False,
        },
    ]

    op.bulk_insert(notification_types_table, notification_types)

    # New instances don't need this migration so we can skip this.
    # All product instances already had this migration applied and therefore
    # don't need this.
    # In case this migration IS needed - FIRST upgrade to grapes release, THEN
    # upgrade to plum and beyond...
    return


def downgrade():
    pass
