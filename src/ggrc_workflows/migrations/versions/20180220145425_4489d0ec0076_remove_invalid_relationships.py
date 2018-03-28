# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Remove invalid relationships.

Create Date: 2018-02-20 14:54:25.381679
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = '4489d0ec0076'
down_revision = '5d4343dc5f2'

RELATIONSHIPS_WHERE_CLAUSE = """
(
    source_type = "CycleTaskGroupObjectTask" AND
    destination_type IN ("Workflow", "TaskGroupTask", "TaskGroup",
                         "CycleTaskGroupObjectTask", "Assessment",
                         "AssessmentTemplate")
) OR (
    source_type IN ("Workflow", "TaskGroupTask", "TaskGroup",
                    "CycleTaskGroupObjectTask", "Assessment",
                    "AssessmentTemplate") AND
    destination_type = "CycleTaskGroupObjectTask"
)
"""

DELETE_REVISIONS_SQL = """
DELETE FROM revisions
WHERE
    resource_type = "Relationship" AND
    resource_id in (SELECT id FROM relationships WHERE {})
""".format(RELATIONSHIPS_WHERE_CLAUSE)

DELETE_RELATIONSHIPS_SQL = """
DELETE FROM relationships
WHERE {}
""".format(RELATIONSHIPS_WHERE_CLAUSE)


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.execute(DELETE_REVISIONS_SQL)
    op.execute(DELETE_RELATIONSHIPS_SQL)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    pass
