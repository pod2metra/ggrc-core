# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
remove documentation description

Create Date: 2018-01-15 10:26:22.153194
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision = '12c716cf3817'
down_revision = '153f98adea4b'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.drop_column('controls', 'documentation_description')


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.add_column('controls',
                  sa.Column(
                      'documentation_description',
                      mysql.TEXT(),
                      nullable=False))
