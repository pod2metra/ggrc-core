# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Recalculate cycle and cycle_task_group end and next due dates and update them

Create Date: 2017-12-04 09:51:03.929341
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = '6a7dbb10dfa'
down_revision = '3e0a6fc71158'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.execute("""
      UPDATE cycle_task_groups g1
      LEFT JOIN (
          SELECT g.id, MAX(t.end_date) AS max_end_date
          FROM cycle_task_groups g
          JOIN cycles c
              ON g.cycle_id = c.id
          LEFT JOIN cycle_task_group_object_tasks t
              ON t.cycle_task_group_id = g.id
          WHERE t.status IN ('Assigned', 'InProgress') OR (
              c.is_verification_needed = 1 AND t.status IN ('Finished'))
          GROUP BY g.id
      ) AS g2
      ON g1.id = g2.id
      SET g1.end_date = g2.max_end_date
  """)

    op.execute("""
      UPDATE cycle_task_groups g1
      LEFT JOIN (
          SELECT g.id, MIN(t.end_date) AS min_end_date
          FROM cycle_task_groups g
          JOIN cycles c
              ON g.cycle_id = c.id
          LEFT JOIN cycle_task_group_object_tasks t
              ON t.cycle_task_group_id = g.id
          WHERE t.end_date > NOW() AND (
              t.status in ('Assigned', 'InProgress') OR (
              c.is_verification_needed = 1 AND t.status IN ('Finished')))
          GROUP BY g.id
      ) AS g2
      ON g1.id = g2.id
      SET g1.next_due_date = g2.min_end_date
  """)

    op.execute("""
      UPDATE cycles c1
      LEFT JOIN (
          SELECT c.id, MAX(g.end_date) AS max_end_date
          FROM cycles c
          JOIN cycle_task_groups g
              ON g.cycle_id = c.id
          WHERE g.status IN ('Assigned', 'InProgress') OR (
              c.is_verification_needed = 1 AND g.status IN ('Finished'))
          GROUP BY c.id
      ) AS c2
      ON c1.id = c2.id
      SET c1.end_date = c2.max_end_date
  """)

    op.execute("""
      UPDATE cycles c1
          LEFT JOIN (
          SELECT c.id, MIN(g.next_due_date) AS min_next_due_date
          FROM cycles c
          JOIN cycle_task_groups g
              ON g.cycle_id = c.id
          WHERE g.end_date > NOW() AND (
              g.status IN ('Assigned', 'InProgress') OR (
              c.is_verification_needed = 1 AND g.status IN ('Finished')))
          GROUP BY c.id
      ) AS c2
      ON c1.id = c2.id
      SET c1.next_due_date = c2.min_next_due_date
  """)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
