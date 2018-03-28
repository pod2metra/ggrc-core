# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Remove invalid context implications

Create Date: 2017-04-05 16:28:26.195655
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = '5a7fd43e43ae'
down_revision = '3ab8b37b04'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.execute("""
      DELETE FROM context_implications WHERE
          context_scope = "Program" AND
          source_context_scope = "Audit"
  """)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
