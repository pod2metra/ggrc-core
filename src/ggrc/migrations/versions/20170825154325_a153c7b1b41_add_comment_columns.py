# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add comment notification columns

Create Date: 2017-08-25 15:43:25.959875
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

from ggrc.migrations.utils.resolve_duplicates import rename_ca_title

revision = 'a153c7b1b41'
down_revision = '55f6307497a6'

table_models = {
    "access_groups": "access_group",
    "clauses": "clause",
    "controls": "control",
    "data_assets": "data_asset",
    "directives": "directive",
    "facilities": "facility",
    "markets": "market",
    "objectives": "objective",
    "org_groups": "org_group",
    "systems": "system",
    "products": "product",
    "sections": "section",
    "vendors": "vendor",
    "issues": "issue",
    "projects": "project",
}


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    # Updates due to added commentable mixin
    for name in table_models.keys():
        op.add_column(name,
                      sa.Column(
                          'recipients', sa.String(length=250), nullable=True))
        op.add_column(name,
                      sa.Column(
                          'send_by_default', sa.Boolean(), nullable=True))
    rename_ca_title("Recipients", table_models.values())
    rename_ca_title("Send by default", table_models.values())


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    # Updates due to added commentable mixin
    for name in table_models.keys():
        op.drop_column(name, 'send_by_default')
        op.drop_column(name, 'recipients')
