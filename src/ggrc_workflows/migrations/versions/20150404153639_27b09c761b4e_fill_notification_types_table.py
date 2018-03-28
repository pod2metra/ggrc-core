# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""fill notification_types table

Revision ID: 27b09c761b4e
Revises: 4f9f00e4faca
Create Date: 2015-04-04 15:36:39.540261

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = '27b09c761b4e'
down_revision = '4f9f00e4faca'


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

    op.bulk_insert(
        notification_types_table,
        [
            # cycle created notifictions
            {
                "name":
                "cycle_created",
                "description":
                ("Notify workflow members that a one time workflow "
                 "has been started and send them their assigned "
                 "tasks."),
                "template":
                "cycle_created",
                "advance_notice":
                0,
                "instant":
                False,
            },
            {
                "name":
                "manual_cycle_created",
                "description":
                ("Notify workflow members that a one time workflow "
                 "has been started and send them their assigned "
                 "tasks."),
                "template":
                "manual_cycle_created",
                "advance_notice":
                0,
                "instant":
                True,
            },

            # cycle task due in notifications
            {
                "name": "cycle_task_due_in",
                "description":
                "Notify task assignee his task is due in X days",
                "template": "cycle_task_due_in",
                "advance_notice": 1,
                "instant": False,
            },
            {
                "name": "one_time_cycle_task_due_in",
                "description":
                "Notify task assignee his task is due in X days",
                "template": "cycle_task_due_in",
                "advance_notice": 1,
                "instant": False,
            },
            {
                "name": "weekly_cycle_task_due_in",
                "description":
                "Notify task assignee his task is due in X days",
                "template": "cycle_task_due_in",
                "advance_notice": 1,
                "instant": False,
            },
            {
                "name": "monthly_cycle_task_due_in",
                "description":
                "Notify task assignee his task is due in X days",
                "template": "cycle_task_due_in",
                "advance_notice": 1,
                "instant": False,
            },
            {
                "name": "quarterly_cycle_task_due_in",
                "description":
                "Notify task assignee his task is due in X days",
                "template": "cycle_task_due_in",
                "advance_notice": 1,
                "instant": False,
            },
            {
                "name": "annually_cycle_task_due_in",
                "description":
                "Notify task assignee his task is due in X days",
                "template": "cycle_task_due_in",
                "advance_notice": 1,
                "instant": False,
            },
            {
                "name": "cycle_task_due_today",
                "description": "Notify task assignee his task is due today",
                "template": "cycle_task_due_today",
                "advance_notice": 0,
                "instant": False,
            },

            # reassigned notifications
            {
                "name": "cycle_task_reassigned",
                "description": "Notify task assignee his task is due today",
                "template": "cycle_task_due_today",
                "advance_notice": 0,
                "instant": True,
            },
            {
                "name": "task_group_assignee_change",
                "description": "Email owners on task group assignee change.",
                "template": "task_group_assignee_change",
                "advance_notice": 0,
                "instant": True,
            },

            # declined
            {
                "name": "cycle_task_declined",
                "description": "Notify task assignee his task is due today",
                "template": "cycle_task_due_today",
                "advance_notice": 0,
                "instant": True,
            },

            # all cycle tasks finished
            {
                "name":
                "all_cycle_tasks_completed",
                "description":
                ("Notify workflow owner when all cycle tasks in one"
                 " cycle have been completed and verified"),
                "template":
                "weekly_workflow_starts_in",
                "advance_notice":
                1,
                "instant":
                True,
            },

            # workflow starts in notifications
            {
                "name": "weekly_workflow_starts_in",
                "description":
                "Advanced notification for a recurring workflow.",
                "template": "weekly_workflow_starts_in",
                "advance_notice": 1,
                "instant": False,
            },
            {
                "name": "monthly_workflow_starts_in",
                "description":
                "Advanced notification for a recurring workflow.",
                "template": "monthly_workflow_starts_in",
                "advance_notice": 3,
                "instant": False,
            },
            {
                "name": "quarterly_workflow_starts_in",
                "description":
                "Advanced notification for a recurring workflow.",
                "template": "quaterly_workflow_starts_in",
                "advance_notice": 7,
                "instant": False,
            },
            {
                "name": "annually_workflow_starts_in",
                "description":
                "Advanced notification for a recurring workflow.",
                "template": "annual_workflow_starts_in",
                "advance_notice": 15,
                "instant": False,
            },
        ])


def downgrade():
    pass
