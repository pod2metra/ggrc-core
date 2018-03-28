# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add test_plan field to set of models

Create Date: 2017-08-23 15:55:49.838780
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

from ggrc.migrations.utils.resolve_duplicates import rename_ca_title

revision = '3897847a6c5c'
down_revision = '2ad7783c176'

table_models = {
    "directives": "directive",
    "sections": "section",
    "objectives": "objective",
    "products": "product",
    "systems": "system",
    "access_groups": "access_group",
    "clauses": "clause",
    "data_assets": "data_asset",
    "facilities": "facility",
    "markets": "market",
    "org_groups": "org_group",
    "projects": "project",
    "vendors": "vendor",
}


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    for table in table_models.keys():
        op.add_column(
            table,
            sa.Column("test_plan", sa.Text, nullable=True),
        )
    rename_ca_title("Assessment Procedure", table_models.values())


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    for table in table_models.keys():
        op.drop_column(table, "test_plan")
