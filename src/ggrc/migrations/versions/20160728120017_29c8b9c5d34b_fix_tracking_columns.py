# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Fix tracking columns (SLOW!)

Create Date: 2016-07-28 12:00:17.948086
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from ggrc.migrations.utils.fix_tracking_columns import (
    upgrade_tables,
    downgrade_tables,
)

# revision identifiers, used by Alembic.
revision = '29c8b9c5d34b'
down_revision = '1269660b288b'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    upgrade_tables("ggrc")


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    downgrade_tables("ggrc")
