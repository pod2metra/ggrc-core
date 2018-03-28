# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
migrate labels

Create Date: 2017-12-19 09:25:14.634542
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = 'f0dade8da1'
down_revision = '1b4c9fd11de1'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.execute("""
      INSERT IGNORE INTO object_labels (label_id,
                                        object_id,
                                        object_type,
                                        created_at,
                                        updated_at)
          (SELECT l.id, a.id, "Assessment", NOW(), NOW()
          FROM assessments a
          JOIN labels l ON a.label=l.name)
  """)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
