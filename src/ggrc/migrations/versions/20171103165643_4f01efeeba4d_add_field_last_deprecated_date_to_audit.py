# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
add field last_deprecated_date to audit

Create Date: 2017-11-03 16:56:43.824168
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '4f01efeeba4d'
down_revision = '3d505e157ab7'


def upgrade():
    """Upgrade database schema - add new field to audits table."""
    op.add_column('audits', sa.Column('last_deprecated_date', sa.Date))
    op.execute("""
      UPDATE audits
      SET last_deprecated_date = DATE(updated_at)
      WHERE status = "Deprecated"
      """)


def downgrade():
    """Downgrade database schema - remove field from audits table"""
    op.drop_column('audits', 'last_deprecated_date')
