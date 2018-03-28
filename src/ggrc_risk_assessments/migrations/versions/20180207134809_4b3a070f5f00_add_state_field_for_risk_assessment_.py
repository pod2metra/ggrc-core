# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
add state field for risk assessment object

Create Date: 2018-02-07 13:48:09.145685
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '4b3a070f5f00'
down_revision = '2d5bf2f9e510'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.add_column('risk_assessments',
                  sa.Column(
                      'status',
                      sa.String(length=250),
                      nullable=False,
                      server_default='Draft'))


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_column("risk_assessments", "status")
