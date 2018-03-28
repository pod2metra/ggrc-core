# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add test_plan field

Create Date: 2017-08-23 16:27:55.094736
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

from ggrc.migrations.utils.resolve_duplicates import rename_ca_title

revision = '5aa9ec7105d1'
down_revision = '4e90a7e4907c'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    for table in ["risks", "threats"]:
        op.add_column(
            table,
            sa.Column("test_plan", sa.Text, nullable=True),
        )
    rename_ca_title("Assessment Procedure", ["risk", "threat"])


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    for table in ["risks", "threats"]:
        op.drop_column(table, "test_plan")
