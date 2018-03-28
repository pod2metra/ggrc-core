# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Update non_editable field for ACR

Create Date: 2017-07-26 13:37:04.807643
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa
from sqlalchemy import and_
from sqlalchemy.sql import table, column
from alembic import op

revision = '163457f4ce13'
down_revision = '377d935e1b21'

NON_EDITABLE_ROLES = {
    "Primary Contacts",
    "Secondary Contacts",
    "Admin",
}
OBJECTS_TO_UPDATE = [
    'Risk',
    'Threat',
]
acr_table = table("access_control_roles", column('name', sa.String),
                  column('object_type', sa.String),
                  column('non_editable', sa.Boolean))


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.execute(acr_table.update().values(non_editable=True).where(
        and_(
            acr_table.c.name.in_(NON_EDITABLE_ROLES),
            acr_table.c.object_type.in_(OBJECTS_TO_UPDATE),
        )))


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.execute(acr_table.update().values(non_editable=False).where(
        and_(
            acr_table.c.name.in_(NON_EDITABLE_ROLES),
            acr_table.c.object_type.in_(OBJECTS_TO_UPDATE),
        )))
