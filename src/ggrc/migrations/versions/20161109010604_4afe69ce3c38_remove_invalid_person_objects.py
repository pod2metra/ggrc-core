# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Remove invalid person objects

Create Date: 2016-11-09 01:06:04.745331
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = '4afe69ce3c38'
down_revision = '2105a9db99fc'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.execute("""DELETE FROM object_people WHERE personable_type IN (
          'InterviewResponse',
          'DocumentationResponse'
      )""")


def downgrade():
    """Nothing to be done about removed data."""
