# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Fix wrong recipients

Create Date: 2017-11-24 11:12:04.455535
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = '3911f39325b4'
down_revision = '3c69a1e45812'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.execute("""
      UPDATE assessments
      SET recipients = ''
      WHERE recipients RLIKE '^,+$';
  """)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    # We can't change recients back as we don't know what item was empty
    # at first and what not (also there is no sense to do it).
