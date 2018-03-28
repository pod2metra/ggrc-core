# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add 'Effective Date' and 'Last Deprecated Date' fields for Objective

Create Date: 2018-03-26 09:47:41.713297
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '9e44253512f2'
down_revision = 'd1671a8dac7'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.add_column('objectives',
                  sa.Column('last_deprecated_date', sa.Date(), nullable=True))
    op.add_column('objectives',
                  sa.Column('start_date', sa.Date(), nullable=True))
    op.execute("""
      UPDATE objectives
      SET last_deprecated_date = DATE(updated_at)
      WHERE status = "Deprecated"
  """)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_column('objectives', 'start_date')
    op.drop_column('objectives', 'last_deprecated_date')
