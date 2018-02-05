# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
Add model names

Create Date: 2018-02-05 07:22:52.109918
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

from ggrc.models import all_models


# revision identifiers, used by Alembic.
revision = '29c75c92298b'
down_revision = 'ef23f2eaf4f'


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  op.execute(
      "INSERT INTO models (name) values {}".format(
          ",".join(
              ['("{}")'.format(m.__name__) for m in all_models.all_models]
          )
      )
  )


def downgrade():
  """Downgrade database schema and/or data back to the previous revision."""
  op.execute("TRUNCATE models")
  pass
