# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add default_to_current_user to AccessControlRole

Create Date: 2017-07-19 09:17:18.030979
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name
import sqlalchemy as sa
from sqlalchemy.sql import text

from alembic import op

revision = '3aeaadf61cb4'
down_revision = '281fea549981'

DEFAULT_ROLE = 'Admin'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.add_column('access_control_roles',
                  sa.Column(
                      'default_to_current_user',
                      sa.Boolean(),
                      nullable=False,
                      server_default="0"))

    connection = op.get_bind()
    connection.execute(
        text("""
      UPDATE access_control_roles
      SET default_to_current_user = 1
      WHERE name = :role;
  """),
        role=DEFAULT_ROLE)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_column('access_control_roles', 'default_to_current_user')
