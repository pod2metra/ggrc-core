# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Update revision content field.

Create Date: 2017-01-12 11:22:54.998164
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from alembic import op

# revision identifiers, used by Alembic.
revision = '177a979b230a'
down_revision = '275cd0dcaea'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.alter_column(
        "revisions",
        "content",
        existing_type=sa.Text(),
        type_=mysql.LONGTEXT,
        nullable=False)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.alter_column(
        "revisions",
        "content",
        existing_type=mysql.LONGTEXT,
        type_=sa.Text(),
        nullable=False)
