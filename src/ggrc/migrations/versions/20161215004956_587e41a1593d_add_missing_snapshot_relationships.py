# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add missing snapshot relationships.

Create Date: 2016-12-15 00:49:56.561951
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = '587e41a1593d'
down_revision = '2a5a39600741'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.execute("""
      insert ignore into relationships (
          modified_by_id,
          created_at,
          updated_at,
          source_id,
          source_type,
          destination_id,
          destination_type
      )
      select
          modified_by_id,
          created_at,
          updated_at,
          parent_id as source_id,
          parent_type as source_type,
          child_id as destination_id,
          child_type as destination_type
      from snapshots
      """)


def downgrade():
    """Ignore downgrade."""
