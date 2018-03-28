# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add Assignee roles to Task and Cycle Task types

Create Date: 2017-10-05 11:45:32.172481
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import datetime

from alembic import op

import sqlalchemy as sa
from sqlalchemy.sql import column
from sqlalchemy.sql import table

# revision identifiers, used by Alembic.
revision = '251191c050d0'
down_revision = '4131bd4a8a4d'

ACR_TABLE = table(
    'access_control_roles',
    column('name', sa.String),
    column('object_type', sa.String),
    column('created_at', sa.DateTime),
    column('updated_at', sa.DateTime),
    column('mandatory', sa.Boolean),
    column('non_editable', sa.Boolean),
    column('delete', sa.Boolean),
    column('my_work', sa.Boolean),
)

INSERT_ACL_ENTRIES = """
INSERT INTO access_control_list
    (person_id, object_id, ac_role_id, object_type, created_at, updated_at)
SELECT t.contact_id, t.id, r.id, r.object_type, now(), now()
FROM task_group_tasks as t
JOIN access_control_roles as r on r.object_type = "TaskGroupTask"
WHERE t.contact_id IS NOT NULL and r.name = "Task Assignees"
UNION ALL
SELECT t.contact_id, t.id, r.id, r.object_type, now(), now()
FROM cycle_task_group_object_tasks as t
JOIN access_control_roles as r on r.object_type = "CycleTaskGroupObjectTask"
where t.contact_id IS NOT NULL AND r.name = "Task Assignees";
"""

DELETE_SQL = """
DELETE acr, acl
FROM access_control_roles AS acr
INNER JOIN access_control_list AS acl
WHERE
    acl.ac_role_id = acr.id AND
    acr.name = "Task Assignees" AND (
        acr.object_type = "TaskGroupTask" OR
        acr.object_type = "CycleTaskGroupObjectTask"
    )
"""


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.bulk_insert(ACR_TABLE, [{
        'name': "Task Assignees",
        'object_type': "TaskGroupTask",
        'created_at': datetime.datetime.now(),
        'updated_at': datetime.datetime.now(),
        'mandatory': True,
        'non_editable': True,
        'delete': False,
        'my_work': False,
    }, {
        'name': "Task Assignees",
        'object_type': "CycleTaskGroupObjectTask",
        'created_at': datetime.datetime.now(),
        'updated_at': datetime.datetime.now(),
        'mandatory': True,
        'non_editable': True,
        'delete': False,
        'my_work': False,
    }])
    op.execute(INSERT_ACL_ENTRIES)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.execute(DELETE_SQL)
