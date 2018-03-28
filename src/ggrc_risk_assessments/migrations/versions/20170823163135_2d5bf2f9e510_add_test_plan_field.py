# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add test_plan field

Create Date: 2017-08-23 16:31:35.304942
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

from ggrc.migrations.utils.resolve_duplicates import rename_ca_title

revision = '2d5bf2f9e510'
down_revision = '237ccd7c769c'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.add_column(
        "risk_assessments",
        sa.Column("test_plan", sa.Text, nullable=True),
    )
    rename_ca_title("Assessment Procedure", ["risk_assessment"])


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_column("risk_assessments", "test_plan")
