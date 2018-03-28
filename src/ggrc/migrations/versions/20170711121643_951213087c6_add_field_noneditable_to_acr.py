# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add field 'non-editable' to access_control_roles

Create Date: 2017-07-11 12:16:43.529661
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa
from sqlalchemy import and_
from sqlalchemy.sql import table, column
from alembic import op

revision = '951213087c6'
down_revision = '33f77e0b029c'

NON_EDITABLE_ROLES = {
    "Admin",
    "Primary Contacts",
    "Secondary Contacts",
}
NON_EDITABLE_CONTROL_ROLES = {
    "Principal Assignees",
    "Secondary Assignees",
}


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.add_column('access_control_roles',
                  sa.Column(
                      'non_editable',
                      sa.Boolean(),
                      nullable=False,
                      server_default="0"))

    acr_table = table("access_control_roles", column('object_type', sa.String),
                      column('name', sa.String),
                      column('non_editable', sa.Boolean))

    op.execute(acr_table.update().values(non_editable=True).where(
        acr_table.c.name.in_(NON_EDITABLE_ROLES)))

    op.execute(acr_table.update().values(non_editable=True).where(
        and_(
            acr_table.c.object_type == "Control",
            acr_table.c.name.in_(NON_EDITABLE_CONTROL_ROLES),
        )))


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_column('access_control_roles', 'non_editable')
