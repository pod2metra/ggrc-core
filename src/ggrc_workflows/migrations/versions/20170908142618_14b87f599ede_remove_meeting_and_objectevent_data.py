# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Remove Meeting and ObjectEvent data

Create Date: 2017-09-08 14:26:18.104984
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

from ggrc.migrations.utils import cleanup

# revision identifiers, used by Alembic.
revision = '14b87f599ede'
down_revision = '6a7dbb10dfa'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    cleanup.delete(op, "task_group_objects", "object_type", value="Meeting")
    cleanup.delete(
        op, "task_group_objects", "object_type", value="ObjectEvent")


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    pass
