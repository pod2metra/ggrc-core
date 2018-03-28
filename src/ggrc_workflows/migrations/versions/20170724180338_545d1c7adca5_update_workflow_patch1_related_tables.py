# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Update workflow related DB tables for workflow-patch1 release

Create Date: 2017-07-24 18:03:38.781339
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '545d1c7adca5'
down_revision = '396f47dcc433'

DAY_UNIT = 'day'
WEEK_UNIT = 'week'
MONTH_UNIT = 'month'
VALID_UNITS = (DAY_UNIT, WEEK_UNIT, MONTH_UNIT)


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    # Add new columns to 'workflows' table
    op.add_column('workflows',
                  sa.Column(
                      'repeat_every',
                      sa.Integer,
                      nullable=True,
                      server_default=None))
    op.add_column('workflows',
                  sa.Column(
                      'unit',
                      sa.Enum(*VALID_UNITS),
                      nullable=True,
                      server_default=None))
    op.add_column('workflows',
                  sa.Column(
                      'repeat_multiplier',
                      sa.Integer,
                      nullable=False,
                      server_default='0'))
    op.create_index('ix_workflows_unit', 'workflows', ['unit'])


def downgrade():
    """"Downgrade database schema and/or data back to the previous revision."""
    op.drop_column('workflows', 'repeat_multiplier')
    op.drop_column('workflows', 'unit')
    op.drop_column('workflows', 'repeat_every')
