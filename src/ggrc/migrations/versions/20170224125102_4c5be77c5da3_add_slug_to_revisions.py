# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add slug to revisions

Create Date: 2017-02-24 12:51:02.131671
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4c5be77c5da3"
down_revision = "341f8a645b2f"


def upgrade():
    """Add resource_slug to revisions table."""
    op.add_column("revisions",
                  sa.Column(
                      "resource_slug", sa.String(length=250), nullable=True))
    op.create_index(
        "ix_revisions_resource_slug",
        "revisions",
        ["resource_slug"],
        unique=False,
    )


def downgrade():
    """Remove resource_slug from revisions table."""
    op.drop_column("revisions", "resource_slug")
