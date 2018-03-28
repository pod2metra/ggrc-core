# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Update invalid task dates

Revision ID: 18bdb0671010
Revises: e81da7a55e7
Create Date: 2015-11-07 01:48:37.046586

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = '18bdb0671010'
down_revision = 'e81da7a55e7'


def upgrade():
    """ Fix all broken task group dates

  This is the easiest solution for solving bad dates that might have been
  imported (such as 12/31/15). We can assume that such data is not in
  production. Setting today's date is still less wrong than having a 2000 year
  old task that might break the app.
  """

    op.execute("""
      UPDATE task_group_tasks
      SET start_date = CURDATE(), end_date=CURDATE()
      WHERE (start_date IS NOT NULL AND start_date < "1900-01-01") OR
            (end_date IS NOT NULL AND end_date < "1900-01-01")
  """)


def downgrade():
    """ We won't currupt the data on downgrade """
    pass
