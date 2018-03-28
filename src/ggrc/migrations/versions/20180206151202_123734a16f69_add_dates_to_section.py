# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add dates to Section

Create Date: 2018-02-06 15:12:02.048376
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '123734a16f69'
down_revision = '4303f98eec2c'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.add_column('sections',
                  sa.Column('last_deprecated_date', sa.Date(), nullable=True))
    op.add_column('sections', sa.Column(
        'start_date', sa.Date(), nullable=True))
    op.execute("""
      UPDATE sections
      SET last_deprecated_date = DATE(updated_at)
      WHERE status = "Deprecated"
  """)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_column('sections', 'start_date')
    op.drop_column('sections', 'last_deprecated_date')
