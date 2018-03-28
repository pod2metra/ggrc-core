# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Update event enum field

Create Date: 2016-09-01 12:57:10.984592
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '173b800a28f3'
down_revision = '31fbfc1bc608'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.alter_column(
        'events',
        'action',
        type_=sa.Enum(u'POST', u'PUT', u'DELETE', u'IMPORT', u'BULK', u'GET'),
        existing_type=sa.Enum(u'POST', u'PUT', u'DELETE', u'IMPORT', u'GET'),
        nullable=False)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.alter_column(
        'events',
        'action',
        type_=sa.Enum(u'POST', u'PUT', u'DELETE', u'IMPORT', u'GET'),
        existing_type=sa.Enum(u'POST', u'PUT', u'DELETE', u'IMPORT', u'BULK',
                              u'GET'),
        nullable=False)
