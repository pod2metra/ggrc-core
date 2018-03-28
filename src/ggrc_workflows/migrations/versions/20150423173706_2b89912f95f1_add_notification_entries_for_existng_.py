# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""add notification entries for existng workflows

Revision ID: 2b89912f95f1
Revises: 27b09c761b4e
Create Date: 2015-04-23 17:37:06.366115

"""

from ggrc import db
from ggrc.models import Notification
from ggrc_workflows.notification import pusher

# revision identifiers, used by Alembic.
revision = '2b89912f95f1'
down_revision = '27b09c761b4e'


def upgrade():
    # New instances don't need this migration so we can skip this.
    # All product instances already had this migration applied and therefore
    # don't need this.
    # In case this migration IS needed - FIRST upgrade to grapes release, THEN
    # upgrade to plum and beyond...
    return


def downgrade():
    delete_types_list = [
        "cycle_task_due_in",
        "one_time_cycle_task_due_in",
        "weekly_cycle_task_due_in",
        "monthly_cycle_task_due_in",
        "quarterly_cycle_task_due_in",
        "annually_cycle_task_due_in",
        "cycle_task_due_today",
        "weekly_workflow_starts_in",
        "monthly_workflow_starts_in",
        "quarterly_workflow_starts_in",
        "annually_workflow_starts_in",
    ]

    for delete_type in delete_types_list:
        notif_type = pusher.get_notification_type(delete_type)
        Notification.query.filter(
            Notification.notification_type == notif_type).delete()

    db.session.commit()
