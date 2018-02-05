# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
Alter definition type id for CADs

Create Date: 2018-02-05 07:53:32.723931
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name


from alembic import op

from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = '2837c8dceab9'
down_revision = '54db0a0aa393'


def upgrade():
  op.alter_column(
      'custom_attribute_definitions',
      'definition_type_id',
      existing_type=mysql.INTEGER(display_width=11),
      nullable=False)


def downgrade():
  op.alter_column(
      'custom_attribute_definitions',
      'definition_type_id',
      existing_type=mysql.INTEGER(display_width=11),
      nullable=True)
