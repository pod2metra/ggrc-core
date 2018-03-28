# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Migrate requests change logs

Create Date: 2017-01-30 06:04:09.538516
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = '57940269e30'
down_revision = '562ec606ff7c'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.execute("""
      update revisions
             join requests on revisions.resource_type = 'Request' and
                              revisions.resource_id = requests.id
             join assessments on requests.slug = assessments.slug
      set resource_type = 'Assessment',
          resource_id = assessments.id
  """)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    pass
