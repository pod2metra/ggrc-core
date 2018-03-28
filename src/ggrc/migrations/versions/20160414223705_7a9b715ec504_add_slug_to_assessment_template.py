# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add slug to assessment template

Create Date: 2016-04-14 22:37:05.135072
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

from sqlalchemy.sql import column
from sqlalchemy.sql import func
from sqlalchemy.sql import table

# revision identifiers, used by Alembic.
revision = "7a9b715ec504"
down_revision = "4e9b71cece04"


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.add_column("assessment_templates",
                  sa.Column("slug", sa.String(length=250), nullable=False))
    assessment_templates_table = table("assessment_templates",
                                       column('id', sa.Integer),
                                       column('slug', sa.Integer))

    op.execute(assessment_templates_table.update().values(
        slug=func.concat(
            op.inline_literal("TEMPLATE-"),
            assessment_templates_table.c.id,
        ), ))


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_column("assessment_templates", "slug")
