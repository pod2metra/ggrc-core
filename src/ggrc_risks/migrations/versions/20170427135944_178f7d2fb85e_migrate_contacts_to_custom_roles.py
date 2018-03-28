# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Migrate contacts to custom_roles

Create Date: 2017-04-27 13:59:44.799279
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from ggrc.migrations.utils.migrate_contacts import migrate_contacts

# revision identifiers, used by Alembic.
revision = '178f7d2fb85e'
down_revision = '1beadffdc8ac'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    tables = [
        ('Risk', 'risks'),
        ('Threat', 'threats'),
    ]
    for type_, table_type in tables:
        migrate_contacts(type_, table_type)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    pass
