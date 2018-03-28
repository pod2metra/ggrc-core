# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
add is_verification_neede to WF and Cycle

Create Date: 2017-06-21 15:04:39.108749
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '50788b66dcd4'
down_revision = '30ea07e9d452'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.add_column("workflows",
                  sa.Column(
                      "is_verification_needed",
                      sa.Boolean(),
                      nullable=False,
                      default=True,
                  ))
    op.add_column("cycles",
                  sa.Column(
                      "is_verification_needed",
                      sa.Boolean(),
                      nullable=False,
                      default=True,
                  ))
    op.execute("""Update workflows set is_verification_needed = true;""")
    op.execute("""Update cycles set is_verification_needed = true;""")


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_column("workflows", "is_verification_needed")
    op.drop_column("cycles", "is_verification_needed")
