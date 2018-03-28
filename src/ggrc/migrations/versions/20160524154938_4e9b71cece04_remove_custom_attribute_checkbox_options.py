# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Remove custom attribute checkbox options

Checkbox options are no longer applicable for checkbox custom attributes.

Create Date: 2016-05-24 15:49:38.105404
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = '4e9b71cece04'
down_revision = '44ebc240800b'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.execute("""
      UPDATE custom_attribute_definitions
      SET multi_choice_options = NULL
      WHERE attribute_type = "Checkbox"
      """)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    pass
