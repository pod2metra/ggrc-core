# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
add Rework Needed status for assessment

Create Date: 2017-09-08 14:05:44.404834
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '3e7c7f3d9308'
down_revision = '3897847a6c5c'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.alter_column(
        'assessments',
        'status',
        type_=sa.Enum("Not Started", "In Progress", "In Review", "Verified",
                      "Completed", "Deprecated", "Rework Needed"),
        existing_type=sa.Enum(
            "Not Started",
            "In Progress",
            "In Review",
            "Verified",
            "Completed",
            "Deprecated",
        ),
        nullable=False,
        server_default="Not Started",
    )


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.execute("UPDATE assessments SET status = 'In Progress' "
               "WHERE status = 'Rework Needed'")
    op.alter_column(
        'assessments',
        'status',
        type_=sa.Enum(
            "Not Started",
            "In Progress",
            "In Review",
            "Verified",
            "Deprecated",
            "Completed",
        ),
        existing_type=sa.Enum(
            "Not Started",
            "In Progress",
            "In Review",
            "Verified",
            "Completed",
            "Deprecated",
            "Rework Needed",
        ),
        nullable=False,
        server_default="Not Started",
    )
