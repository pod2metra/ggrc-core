# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
add is external column to relationships table

Create Date: 2018-02-13 10:38:10.322322
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'd1671a8dac7'
down_revision = '40d92baab48c'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.add_column('relationships',
                  sa.Column(
                      'is_external',
                      sa.Boolean(),
                      nullable=False,
                      default=False))


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_column('relationships', 'is_external')
