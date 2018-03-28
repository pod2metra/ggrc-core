# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add url and reference_url columns

Create Date: 2016-05-13 13:51:06.534663
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '47bf3f1f9be8'
down_revision = '17ae137bda7a'


def upgrade():
    """Add url and reference_url columns"""

    op.add_column("risks",
                  sa.Column("url", sa.String(length=250), nullable=True))
    op.add_column("risks",
                  sa.Column(
                      "reference_url", sa.String(length=250), nullable=True))


def downgrade():
    op.drop_column("risks", "url")
    op.drop_column("risks", "reference_url")
