# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Remove invalid revision hash

Create Date: 2017-01-06 08:03:58.016264
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = '353e5f281799'
down_revision = '1aa39778da75'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.execute("""
      truncate ggrc_alembic_version
  """)
    op.execute("""
      insert into ggrc_alembic_version
      values ('{}')
  """.format(down_revision))


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    pass
