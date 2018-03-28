# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Remove gGRC Admin hardcoded permissions

Create Date: 2016-06-10 07:10:22.781593
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op
from sqlalchemy.sql import table, column
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "5208a8371512"
down_revision = "1d98cee15705"

roles_table = table(
    "roles",
    column("name", sa.String),
    column("permissions_json", sa.Text),
)


def upgrade():
    """Change gGRC Admin's permissions to code declared."""
    op.execute(roles_table.update().where(roles_table.c.name == "gGRC Admin")
               .values(permissions_json="CODE DECLARED ROLE"))


def downgrade():
    """Revert gGRC Admin's permissions to DB defined."""
    op.execute(
        roles_table.update().where(roles_table.c.name == "gGRC Admin")
        .values(permissions_json="""{"__GGRC_ADMIN__": ["__GGRC_ALL__"]}"""))
