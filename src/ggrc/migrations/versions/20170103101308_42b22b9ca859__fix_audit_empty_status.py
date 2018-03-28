# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Fix audit empty status

Create Date: 2016-12-22 13:53:24.497701
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '42b22b9ca859'
down_revision = '4fcaef05479f'

VALID_STATES = (u'Planned', u'In Progress', u'Manager Review',
                u'Ready for External Review', u'Completed')


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.execute("UPDATE audits SET status='Planned' WHERE status=0")
    op.alter_column(
        'audits',
        'status',
        nullable=True,
        type_=sa.String(250),
        existing_type=sa.Enum(*VALID_STATES))


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.alter_column(
        'audits',
        'status',
        nullable=False,
        type_=sa.Enum(*VALID_STATES),
        existing_type=sa.String)
