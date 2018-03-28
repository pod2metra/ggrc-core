# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add comment columns

Create Date: 2017-08-25 15:44:01.609065
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

from ggrc.migrations.utils.resolve_duplicates import rename_ca_title

revision = '4e90a7e4907c'
down_revision = '163457f4ce13'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    # Updates due to added commentable mixin
    for table in ["risks", "threats"]:
        op.add_column(table,
                      sa.Column(
                          'recipients', sa.String(length=250), nullable=True))
        op.add_column(table,
                      sa.Column(
                          'send_by_default', sa.Boolean(), nullable=True))
    rename_ca_title("Recipients", ["risks", "threats"])
    rename_ca_title("Send by default", ["risks", "threats"])


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    # Updates due to added commentable mixin
    for table in ["risks", "threats"]:
        op.drop_column(table, 'send_by_default')
        op.drop_column(table, 'recipients')
