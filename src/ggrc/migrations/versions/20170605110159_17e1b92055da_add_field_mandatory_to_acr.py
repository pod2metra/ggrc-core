# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add field 'mandatory' to access_control_roles

Create Date: 2017-06-05 11:01:59.066792
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '17e1b92055da'
down_revision = '59d9fbfb42dc'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.add_column('access_control_roles',
                  sa.Column(
                      'mandatory',
                      sa.Boolean(),
                      nullable=False,
                      server_default="0"))


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_column('access_control_roles', 'mandatory')
