# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
empty message

Create Date: 2017-10-11 13:46:54.015780
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op


# revision identifiers, used by Alembic.
revision = '12d03f1131a5'
down_revision = '251191c050d0'

INSERT_SQL = """
INSERT INTO access_control_list
    (person_id, object_id, ac_role_id, object_type, created_at, updated_at)
SELECT t.contact_id, t.id, r.id, r.object_type, now(), now()
FROM task_group_tasks as t
JOIN access_control_roles as r on r.object_type = "TaskGroupTask"
WHERE t.contact_id IS NOT NULL and r.name = "Assignee"
UNION ALL
SELECT t.contact_id, t.id, r.id, r.object_type, now(), now()
FROM cycle_task_group_object_tasks as t
JOIN access_control_roles as r on r.object_type = "CycleTaskGroupObjectTask"
where t.contact_id IS NOT NULL AND r.name = "Assignee";
"""

DELETE_SQL = """
DELETE a FROM access_control_list AS a
JOIN access_control_roles AS r on r.id = a.ac_role_id
WHERE r.name = "Assignee"   AND (
      r.object_type = "TaskGroupTask" OR
      r.object_type = "CycleTaskGroupObjectTask");
"""


def upgrade():
  op.execute(INSERT_SQL)


def downgrade():
  op.execute(DELETE_SQL)
