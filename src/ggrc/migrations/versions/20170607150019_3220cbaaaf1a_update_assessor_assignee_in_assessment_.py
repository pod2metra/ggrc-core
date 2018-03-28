# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Update assessor -> assignee in assessment template

Create Date: 2017-06-07 15:00:19.313191
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = '3220cbaaaf1a'
down_revision = '17e1b92055da'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.execute('UPDATE assessment_templates '
               'SET default_people = REPLACE(default_people, '
               '"Secondary Assessors", "Secondary Assignees") '
               'where default_people like "%Secondary Assessors%";')

    op.execute('UPDATE assessment_templates '
               'SET default_people = REPLACE(default_people, '
               '"Primary Assessor", "Primary Assignees") '
               'where default_people like "%Primary Assessor%";')


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    pass
