# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
add folder fields

Create Date: 2017-07-25 13:22:06.626094
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = 'ba01ec28bff'
down_revision = '191c7cc1fed8'

TABLES = ('programs', 'audits', 'controls', )


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  for table in TABLES:
    op.add_column(table, sa.Column('folder', sa.Text(), nullable=True))


def downgrade():
  """Downgrade database schema and/or data back to the previous revision."""
  for table in TABLES:
    op.drop_column(table, 'folder')
