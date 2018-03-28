# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Rename Test Plan to Assessment Procedure

Create Date: 2017-09-11 16:19:13.579561
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name
# revision identifiers, used by Alembic.
from ggrc.app import app
from ggrc.migrations.utils.resolve_duplicates import rename_ca_title

revision = '2cdde3aa3844'
down_revision = '2ada007df3ee'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    with app.app_context():
        rename_ca_title("Assessment Procedure",
                        ["assessment", "assessment_template", "control"])
        rename_ca_title("Use Control Assessment Procedure",
                        ["assessment_template"])


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    # Renamed CAs can't be rolled back as we don't know
    # which of them were renamed.
