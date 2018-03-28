# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Set Administrator UserRoles context to 0

Create Date: 2018-01-25 14:10:11.112025
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = '568f400e4a62'
down_revision = '1035f388d822'


def upgrade():
    """Fix context_id for UserRole where role=Admin.

  This context_id is special and should be used only for Admins.
  """
    op.execute("""
      UPDATE user_roles
      JOIN roles ON user_roles.role_id = roles.id
      SET user_roles.context_id = 0
      WHERE user_roles.context_id is NULL AND
            roles.name = 'Administrator'
  """)


def downgrade():
    pass
