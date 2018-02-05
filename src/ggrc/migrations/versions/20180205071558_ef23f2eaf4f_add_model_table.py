# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
Add model table

Create Date: 2018-02-05 07:15:58.179139
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'ef23f2eaf4f'
down_revision = '21db8dd549ac'


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  op.create_table(
      'models',
      sa.Column('id', sa.Integer(), nullable=False),
      sa.Column('name', sa.String(length=250), nullable=False),
      sa.PrimaryKeyConstraint('id'),
      sa.UniqueConstraint('name'),
  )
  op.add_column(
      'custom_attribute_definitions',
      sa.Column(
          'definition_type_id',
          sa.Integer(),
          nullable=True,
      ),
  )


def downgrade():
  """Downgrade database schema and/or data back to the previous revision."""
  op.drop_column('custom_attribute_definitions', 'definition_type_id')
  op.drop_table('models')
