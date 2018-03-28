# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add archived column to audits

Create Date: 2017-05-09 14:24:44.545080
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '4936d6e2f8dd'
down_revision = '3220cbaaaf1a'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.add_column('audits',
                  sa.Column(
                      'archived',
                      sa.Boolean(),
                      nullable=False,
                      server_default="0"))


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_column('audits', 'archived')
