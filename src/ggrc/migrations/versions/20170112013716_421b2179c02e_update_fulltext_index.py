# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Update fulltext index.

Create Date: 2017-01-12 01:37:16.801973
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '421b2179c02e'
down_revision = '177a979b230a'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.alter_column(
        "fulltext_record_properties",
        "property",
        existing_type=sa.String(length=64),
        type_=sa.String(length=250),
        nullable=False)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.alter_column(
        "fulltext_record_properties",
        "property",
        existing_type=sa.String(length=250),
        type_=sa.String(length=64),
        nullable=False)
