# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
add comment roles

Create Date: 2018-02-07 10:23:04.469109
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op


# revision identifiers, used by Alembic.
revision = '1abe4c30a261'
down_revision = '19a260ec358e'


def upgrade():
  op.execute("""
       INSERT INTO access_control_roles
          (name, object_type, `read`, `update`, `delete`,
           non_editable, internal, created_at, updated_at)
       VALUES ('CommentReader', 'Comment', 1, 0, 0, 1, 1, NOW(), NOW());
  """)


def downgrade():
  pass
