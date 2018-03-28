# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Fix Assessment contexts

Create Date: 2017-02-19 22:18:07.518997
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

# revision identifiers, used by Alembic.
revision = '4e7fda17abc7'
down_revision = '2f1cee67a8f3'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    pass


def downgrade():
    """Nothing to do here."""
    pass
