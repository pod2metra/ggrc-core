# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add assessors reminder notification

Create Date: 2016-04-12 13:44:48.265193
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa
from sqlalchemy.sql import column
from sqlalchemy.sql import table
from sqlalchemy.sql import select
from alembic import op

# revision identifiers, used by Alembic.
revision = '11cee57a4149'
down_revision = '50c374901d42'

notifications_table = table(
    'notifications',
    column('id', sa.Integer),
    column('notification_type_id', sa.Integer),
)

notification_types_table = table('notification_types',
                                 column('id', sa.Integer),
                                 column('name', sa.String),
                                 column('description', sa.Text),
                                 column('template', sa.String),
                                 column('instant', sa.Boolean),
                                 column('advance_notice', sa.Integer))


def upgrade():
    """Inserts new notification type"""
    op.bulk_insert(notification_types_table, [{
        "name":
        "assessment_assessor_reminder",
        "description": ("Notify all Assessors that they should take a look "
                        "at the assessment."),
        "template":
        "",
        "advance_notice":
        0,
        "instant":
        False
    }])


def downgrade():
    """First removes notifications and then removes notification type"""
    op.execute(notifications_table.delete().where(
        notifications_table.c.notification_type_id
        == select([notification_types_table.c.id]).where(
            notification_types_table.c.name ==
            "assessment_assessor_reminder")))

    op.execute(notification_types_table.delete().where(
        notification_types_table.c.name == "assessment_assessor_reminder"))
