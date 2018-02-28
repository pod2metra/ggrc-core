# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
deny delete acr and cad

Create Date: 2018-02-28 14:09:40.578697
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op


revision = '3f8cbf3afce6'
down_revision = '19a260ec358e'


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  op.add_column('access_control_roles',
                sa.Column('is_delete_allowed',
                          sa.Boolean(),
                          nullable=False))
  op.add_column('custom_attribute_definitions',
                sa.Column('is_delete_allowed',
                          sa.Boolean(),
                          nullable=False))

def downgrade():
  """Downgrade database schema and/or data back to the previous revision."""
  op.drop_column('custom_attribute_definitions', 'is_delete_allowed')
  op.drop_column('access_control_roles', 'is_delete_allowed')
