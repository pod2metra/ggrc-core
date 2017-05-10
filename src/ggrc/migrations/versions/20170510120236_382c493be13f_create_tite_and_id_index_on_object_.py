# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
create type and id index on object_documents

Create Date: 2017-05-10 12:02:36.178253
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op


# revision identifiers, used by Alembic.
revision = '382c493be13f'
down_revision = '1ac595e94a23'

INX_NAME = "ix_documentable_type_documentable_id"


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  sql = (
      "CREATE INDEX {name} "
      "ON object_documents(documentable_type, documentable_id)"
  ).format(name=INX_NAME)
  op.execute(sql)


def downgrade():
  """Downgrade database schema and/or data back to the previous revision."""
  op.execute("DROP INDEX {name} ON object_documents".format(name=INX_NAME))
