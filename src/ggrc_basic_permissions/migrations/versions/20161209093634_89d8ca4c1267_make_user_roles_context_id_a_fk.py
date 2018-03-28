# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Make user_roles.context_id a FK

Create Date: 2016-12-09 09:36:34.286793
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = "89d8ca4c1267"
down_revision = "4e105fc39b25"


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.execute("""
      delete from user_roles where context_id not in (select id from contexts)
  """)
    op.create_foreign_key("fk_user_roles_contexts", "user_roles", "contexts",
                          ["context_id"], ["id"])


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_constraint(
        "fk_user_roles_contexts", "user_roles", type_="foreignkey")
