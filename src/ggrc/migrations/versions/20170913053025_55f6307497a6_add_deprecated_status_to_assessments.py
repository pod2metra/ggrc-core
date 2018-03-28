# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add Deprecated to assessments status

Create Date: 2017-09-13 05:30:25.279068
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '55f6307497a6'
down_revision = '42a022944c03'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.alter_column(
        'assessments',
        'status',
        type_=sa.Enum("Not Started", "In Progress", "In Review", "Verified",
                      "Completed", "Deprecated"),
        existing_type=sa.Enum("Not Started", "In Progress", "In Review",
                              "Verified", "Completed"),
        nullable=False,
        server_default="Not Started",
    )


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.alter_column(
        'assessments',
        'status',
        type_=sa.Enum(
            "Not Started",
            "In Progress",
            "In Review",
            "Verified",
            "Completed",
        ),
        existing_type=sa.Enum("Not Started", "In Progress", "In Review",
                              "Verified", "Completed"
                              "Deprecated"),
        nullable=False,
        server_default="Not Started",
    )
