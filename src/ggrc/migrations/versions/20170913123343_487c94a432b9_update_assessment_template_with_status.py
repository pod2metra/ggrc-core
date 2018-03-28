# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Update AssessmentTemplate with status column

Create Date: 2017-09-13 12:33:43.305853
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op
from ggrc.migrations.utils.resolve_duplicates import rename_ca_title

# revision identifiers, used by Alembic.
revision = '434683ceff87'
down_revision = '2cdde3aa3844'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    rename_ca_title("state", [
        "assessment_template",
    ])
    op.add_column(
        "assessment_templates",
        sa.Column(
            'status',
            sa.String(length=250),
            nullable=False,
            server_default='Draft'),
    )


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_column("assessment_templates", "status")
