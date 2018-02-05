# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
Change defintion type in CADs

Create Date: 2018-02-05 07:35:09.805970
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

from ggrc.models import all_models


# revision identifiers, used by Alembic.
revision = '54db0a0aa393'
down_revision = '29c75c92298b'


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  models = {m._inflector.table_singular: m.__name__
            for m in all_models.all_models}
  op.execute(
      'DELETE from custom_attribute_definitions where definition_type = ""'
  )
  for inflector, model in models.iteritems():
    op.execute(
        'UPDATE custom_attribute_definitions '
        'SET definition_type_id= ( '
        'SELECT m.id FROM models AS m WHERE m.name = "{name}") '
        'WHERE definition_type="{inflector}"'.format(
            name=model,
            inflector=inflector,
        )
    )


def downgrade():
  """Downgrade database schema and/or data back to the previous revision."""
  models = {m._inflector.table_singular: m.__name__
            for m in all_models.all_models}
  for inflector, model in models.iteritems():
    op.execute(
        'UPDATE custom_attribute_definitions '
        'SET definition_type="{inflector}" '
        'WHERE EXISTS ('
        'SELECT 1 FROM models AS m WHERE m.name = "{name}" '
        'and definition_type_id = m.id)'.format(
            name=model,
            inflector=inflector,
        )
    )
