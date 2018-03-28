# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Remove Meeting and ObjectEvent data

Create Date: 2017-09-08 14:26:13.029930
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

from ggrc.migrations.utils import cleanup

# revision identifiers, used by Alembic.
revision = '3c69a1e45812'
down_revision = 'f0dade8da1'

DELETIONS = (
    ("audit_objects", "auditable_type"),
    ("custom_attribute_definitions", "definition_type"),
    ("fulltext_record_properties", "type"),
    ("notifications", "object_type"),
    ("object_people", "personable_type"),
    ("relationships", "source_type"),
    ("relationships", "destination_type"),
)


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    for table, field in DELETIONS:
        cleanup.delete(op, table, field, value="Meeting")
        cleanup.delete(op, table, field, value="ObjectEvent")


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    pass
