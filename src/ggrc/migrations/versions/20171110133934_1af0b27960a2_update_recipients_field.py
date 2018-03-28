# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Update recipients field

Create Date: 2017-11-10 13:39:34.865657
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa
from alembic import op

revision = '1af0b27960a2'
down_revision = '431dcf5c75af'

COMMENTABLE_TABLES = [
    "access_groups", "clauses", "controls", "data_assets", "directives",
    "facilities", "markets", "objectives", "org_groups", "systems", "products",
    "sections", "vendors", "issues", "projects"
]


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    for name in COMMENTABLE_TABLES:
        commentable_table = sa.sql.table(name,
                                         sa.Column(
                                             'recipients',
                                             sa.String(length=250)))
        op.execute(commentable_table.update().values(
            recipients="Admin,Primary Contacts,Secondary Contacts"))


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    for name in COMMENTABLE_TABLES:
        commentable_table = sa.sql.table(name,
                                         sa.Column(
                                             'recipients',
                                             sa.String(length=250)))
        op.execute(commentable_table.update().values(recipients=None))
