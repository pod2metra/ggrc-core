# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add WorkflowEditor permission role

Create Date: 2017-06-26 12:32:11.421317
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '55501ef0f634'
down_revision = '50788b66dcd4'

_NOW = sa.func.now()

roles = sa.sql.table(
    'roles',
    sa.sql.column('name', sa.String),
    sa.sql.column('permissions_json', sa.String),
    sa.sql.column('description', sa.String),
    sa.sql.column('created_at', sa.DateTime),
    sa.sql.column('updated_at', sa.DateTime),
    sa.sql.column('scope', sa.String),
)


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.execute(roles.insert().values({
        "name":
        "WorkflowEditor",
        "permissions_json":
        "CODE DECLARED ROLE",
        "description":
        "This role grants a user permission to edit workflow "
        "mappings and details",
        "created_at":
        _NOW,
        "updated_at":
        _NOW,
        "scope":
        "Workflow Implied"
    }))


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.execute(roles.delete().where(roles.c.name == "WorkflowEditor"))
