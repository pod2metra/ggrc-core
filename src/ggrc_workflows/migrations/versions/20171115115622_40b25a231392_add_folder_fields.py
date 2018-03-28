# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
add folder fields

Create Date: 2017-11-15 11:56:22.738077
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '40b25a231392'
down_revision = '456b7edf6027'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.add_column('workflows',
                  sa.Column('folder', sa.Text(), nullable=False, default=""))


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_column('workflows', sa.Column('folder', sa.Text(), nullable=True))
