# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add comments' owners information.

Create Date: 2016-06-08 13:25:26.635435
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = "170e453da661"
down_revision = "7a9b715ec504"


def upgrade():
    """Create owner information for the existing comments.

  A comment's owner is assumed to be the user who last edited it, and this
  information is added to the object_owners table for all existing comments.

  If a record already exists, do nothing (this could happen e.g. on a DB
  downgrade and a subsequent another upgrade).
  """
    # NOTE: we set the status column's value to "Draft" to be consistent with
    # what the application does when a new comment is created
    command = """
    INSERT IGNORE INTO object_owners (
      person_id, ownable_id, ownable_type, modified_by_id,
      created_at, updated_at, status
    )
    SELECT
      modified_by_id, id, "Comment", modified_by_id, created_at, updated_at,
      "Draft"
    FROM comments;
  """

    op.execute(command)


def downgrade():
    """Do not delete any comments' owner information to preserve data."""
