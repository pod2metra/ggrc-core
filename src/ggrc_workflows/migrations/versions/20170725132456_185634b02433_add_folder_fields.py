# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
add folder fields

Create Date: 2017-07-25 13:24:56.968236
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '185634b02433'
down_revision = '396f47dcc433'


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  op.add_column('workflows', sa.Column('folder', sa.Text(), nullable=True))


def downgrade():
  """Downgrade database schema and/or data back to the previous revision."""
  op.drop_column('workflows', sa.Column('folder', sa.Text(), nullable=True))
