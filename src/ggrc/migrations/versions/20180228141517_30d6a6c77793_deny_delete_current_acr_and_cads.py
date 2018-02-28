# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
deny delete current acr and cads

Create Date: 2018-02-28 14:15:17.020528
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '30d6a6c77793'
down_revision = '3f8cbf3afce6'


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  op.execute("UPDATE access_control_roles set is_delete_allowed=0")
  op.execute("UPDATE custom_attribute_definitions set is_delete_allowed=0")


def downgrade():
  return
