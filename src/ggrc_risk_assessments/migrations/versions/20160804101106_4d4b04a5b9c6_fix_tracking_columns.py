# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Fix tracking columns (SLOW!)

Create Date: 2016-08-04 10:11:06.471654
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from ggrc.migrations.utils.fix_tracking_columns import (
    upgrade_tables,
    downgrade_tables,
)

# revision identifiers, used by Alembic.
revision = '4d4b04a5b9c6'
down_revision = '5b29b4becf8'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    upgrade_tables("ggrc_risk_assessments")


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    downgrade_tables("ggrc_risk_assessments")
