# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Update workflows table, remove 'frequency' column

Create Date: 2017-07-25 09:53:13.210476
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op
from sqlalchemy import case

# revision identifiers, used by Alembic.
revision = '416613a797e4'
down_revision = '545d1c7adca5'

DAY_UNIT = 'day'
WEEK_UNIT = 'week'
MONTH_UNIT = 'month'
VALID_UNITS = (DAY_UNIT, WEEK_UNIT, MONTH_UNIT)

workflows = sa.sql.table(
    'workflows',
    sa.sql.column('frequency', sa.String),
    sa.sql.column('repeat_every', sa.Integer),
    sa.sql.column('unit', sa.Enum(*VALID_UNITS)),
)
notifications = sa.sql.table(
    'notifications',
    sa.sql.column('name', sa.String),
    sa.sql.column("notification_type_id", sa.Integer),
)
notification_types = sa.sql.table(
    'notification_types',
    sa.sql.column('id', sa.Integer),
    sa.sql.column('name', sa.String),
    sa.sql.column('description', sa.Text),
    sa.sql.column('template', sa.String),
    sa.sql.column('instant', sa.Boolean),
    sa.sql.column('advance_notice', sa.Integer),
)


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.execute(
        workflows.update().where(~workflows.c.frequency.is_(None)).values({
            "unit":
            case(
                [
                    (workflows.c.frequency == "one_time", None),
                    (workflows.c.frequency == "weekly", "week"),
                    (workflows.c.frequency == "monthly", "month"),
                    (workflows.c.frequency == "quarterly", "month"),
                    (workflows.c.frequency == "annually", "month"),
                ],
                else_=None),
            "repeat_every":
            case(
                [
                    (workflows.c.frequency == "one_time", None),
                    (workflows.c.frequency == "weekly", 1),
                    (workflows.c.frequency == "monthly", 1),
                    (workflows.c.frequency == "quarterly", 3),
                    (workflows.c.frequency == "annually", 12),
                ],
                else_=None)
        }))

    # migrate notification_types data since it's bound to frequency
    # add day notification_types
    op.bulk_insert(
        notification_types,
        [
            {
                # cycle created notifiction
                "name": "day_cycle_task_due_in",
                "description":
                "Notify task assignee his task is due in X days",
                "template": "cycle_task_due_in",
                "advance_notice": 1,
                "instant": False,
            },
            {
                # workflow starts in notification
                "name": "day_workflow_starts_in",
                "description":
                "Advanced notification for a recurring workflow.",
                "template": "day_workflow_starts_in",
                "advance_notice": 1,
                "instant": False,
            },
        ])

    # modify weekly, monthly notification_types to week, month
    op.execute(notification_types.update().where(
        notification_types.c.name == op.inline_literal(
            'weekly_cycle_task_due_in')).values({
                'name':
                op.inline_literal('week_cycle_task_due_in')
            }))
    op.execute(notification_types.update().where(
        notification_types.c.name == op.inline_literal(
            'monthly_cycle_task_due_in')).values({
                'name':
                op.inline_literal('month_cycle_task_due_in')
            }))
    op.execute(notification_types.update().where(
        notification_types.c.name == op.inline_literal(
            'weekly_workflow_starts_in')).values({
                'name':
                op.inline_literal('week_workflow_starts_in'),
                'template':
                op.inline_literal('week_workflow_starts_in')
            }))
    op.execute(notification_types.update().where(
        notification_types.c.name == op.inline_literal(
            'monthly_workflow_starts_in')).values({
                'name':
                op.inline_literal('month_workflow_starts_in'),
                'template':
                op.inline_literal('month_workflow_starts_in')
            }))

    # migrate notification_types in notifications with types being deleted
    # quarterly_, annually_ -> month_
    cycle_types_list = [
        "quarterly_cycle_task_due_in",
        "annually_cycle_task_due_in",
    ]
    workflow_types_list = [
        "quarterly_workflow_starts_in",
        "annually_workflow_starts_in",
    ]
    op.execute(notifications.update().where(
        notifications.c.notification_type_id.in_(
            sa.sql.select([notification_types.c.id]).where(
                notification_types.c.name.in_(cycle_types_list)))).values({
                    "notification_type_id":
                    sa.sql.select([
                        notification_types.c.id
                    ]).where(notification_types.c.name == op.inline_literal(
                        'month_cycle_task_due_in')),
                }))
    op.execute(notifications.update().where(
        notifications.c.notification_type_id.in_(
            sa.sql.select([notification_types.c.id]).where(
                notification_types.c.name.in_(workflow_types_list)))).values({
                    "notification_type_id":
                    sa.sql.select([
                        notification_types.c.id
                    ]).where(notification_types.c.name == op.inline_literal(
                        'month_workflow_starts_in')),
                }))

    # delete deprecated notification_types
    op.execute(notification_types.delete().where(
        notification_types.c.name.in_(cycle_types_list + workflow_types_list)))


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    # migrate notification_types in notifications with types being deleted
    # day_ -> month_
    delete_types_list = [
        "day_cycle_task_due_in",
        "day_workflow_starts_in",
    ]
    cycle_types_list = [
        "quarterly_cycle_task_due_in",
        "annually_cycle_task_due_in",
    ]
    workflow_types_list = [
        "quarterly_workflow_starts_in",
        "annually_workflow_starts_in",
    ]
    op.execute(notifications.update().where(
        notifications.c.notification_type_id.in_(
            sa.sql.select([notification_types.c.id]).where(
                notification_types.c.name.in_(cycle_types_list)))).values({
                    "notification_type_id":
                    sa.sql.select([
                        notification_types.c.id
                    ]).where(notification_types.c.name == op.inline_literal(
                        'month_cycle_task_due_in')),
                }))
    op.execute(notifications.update().where(
        notifications.c.notification_type_id.in_(
            sa.sql.select([notification_types.c.id]).where(
                notification_types.c.name.in_(workflow_types_list)))).values({
                    "notification_type_id":
                    sa.sql.select([
                        notification_types.c.id
                    ]).where(notification_types.c.name == op.inline_literal(
                        'month_workflow_starts_in')),
                }))

    # then delete day_ notification_types
    op.execute(notification_types.delete().where(
        notification_types.c.name.in_(delete_types_list)))

    # modify weekly, monthly notification_types to week, month
    op.execute(notification_types.update().where(
        notification_types.c.name == op.inline_literal(
            'week_cycle_task_due_in')).values({
                'name':
                op.inline_literal('weekly_cycle_task_due_in')
            }))
    op.execute(notification_types.update().where(
        notification_types.c.name == op.inline_literal(
            'month_cycle_task_due_in')).values({
                'name':
                op.inline_literal('monthly_cycle_task_due_in')
            }))
    op.execute(notification_types.update().where(
        notification_types.c.name == op.inline_literal(
            'week_workflow_starts_in')).values({
                'name':
                op.inline_literal('weekly_workflow_starts_in'),
                'template':
                op.inline_literal('weekly_workflow_starts_in')
            }))
    op.execute(notification_types.update().where(
        notification_types.c.name == op.inline_literal(
            'month_workflow_starts_in')).values({
                'name':
                op.inline_literal('monthly_workflow_starts_in'),
                'template':
                op.inline_literal('monthly_workflow_starts_in')
            }))

    # migrate notification_types in notifications with types being deleted
    # we can not recover data precisely after once upgraded, because
    # users could create workflows which do not correspond to old types
    # month_ -> monthly_
    cycle_types_list = [
        "month_cycle_task_due_in",
    ]
    workflow_types_list = [
        "month_workflow_starts_in",
    ]
    op.execute(notifications.update().where(
        notifications.c.notification_type_id.in_(
            sa.sql.select([notification_types.c.id]).where(
                notification_types.c.name.in_(cycle_types_list)))).values({
                    "notification_type_id":
                    sa.sql.select([
                        notification_types.c.id
                    ]).where(notification_types.c.name == op.inline_literal(
                        'monthly_cycle_task_due_in')),
                }))
    op.execute(notifications.update().where(
        notifications.c.notification_type_id.in_(
            sa.sql.select([notification_types.c.id]).where(
                notification_types.c.name.in_(workflow_types_list)))).values({
                    "notification_type_id":
                    sa.sql.select([
                        notification_types.c.id
                    ]).where(notification_types.c.name == op.inline_literal(
                        'monthly_workflow_starts_in')),
                }))

    # delete deprecated notification_types
    op.execute(notification_types.delete().where(
        notification_types.c.name.in_(cycle_types_list + workflow_types_list)))
