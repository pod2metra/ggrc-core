# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Fix Assessment contexts again

Create Date: 2017-02-24 20:28:00.507631
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

# revision identifiers, used by Alembic.
revision = '341f8a645b2f'
down_revision = '4e7fda17abc7'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    pass


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    pass
