# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
setup default_people

Create Date: 2017-08-14 10:49:14.129252
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op


# revision identifiers, used by Alembic.
revision = '295d4ffdb974'
down_revision = '191c7cc1fed8'


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  op.execute(
      'UPDATE assessment_templates '
      'SET default_people = '
      'REPLACE(default_people, "Audit Lead", "Audit Captain") '
      'where default_people like "%Audit Lead%";'
  )


def downgrade():
  """Downgrade database schema and/or data back to the previous revision."""
  op.execute(
      'UPDATE assessment_templates '
      'SET default_people = '
      'REPLACE(default_people, "Audit Captain", "Audit Lead") '
      'where default_people like "%Audit Captain%";'
  )
