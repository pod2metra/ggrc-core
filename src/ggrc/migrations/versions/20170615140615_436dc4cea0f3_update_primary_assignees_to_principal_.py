# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Update primary assignees to principal assignees in assessment template

Create Date: 2017-06-15 14:06:15.179837
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = '436dc4cea0f3'
down_revision = '56108297b924'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.execute(
        'UPDATE assessment_templates '
        'SET default_people = '
        'REPLACE(default_people, "Primary Assignees", "Principal Assignees") '
        'where default_people like "%Primary Assignees%";')
    op.execute(
        'UPDATE assessment_templates '
        'SET default_people = '
        'REPLACE(default_people, "Primary Contact", "Primary Contacts") '
        'where default_people like "%Primary Contact%";')
    op.execute(
        'UPDATE assessment_templates '
        'SET default_people = '
        'REPLACE(default_people, "Primary Contactss", "Primary Contacts") '
        'where default_people like "%Primary Contactss%";')


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    pass
