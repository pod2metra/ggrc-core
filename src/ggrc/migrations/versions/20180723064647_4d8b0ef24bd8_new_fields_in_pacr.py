# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
new fields in pacr

Create Date: 2018-07-23 06:46:47.878601
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '4d8b0ef24bd8'
down_revision = '913f6da9cda8'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'propagated_access_control_roles',
        sa.Column(
            'for_down_path',
            sa.String(length=250),
            nullable=False
        )
    )
    op.add_column(
        'propagated_access_control_roles',
        sa.Column(
            'for_up_path',
            sa.String(length=250),
            nullable=False
        )
    )
    op.drop_column('propagated_access_control_roles', 'for_path')
    # ### end Alembic commands ###

def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('propagated_access_control_roles', 'for_up_path')
    op.drop_column('propagated_access_control_roles', 'for_down_path')
    op.add_column(
        'propagated_access_control_roles',
        sa.Column(
            'for_path',
            sa.String(length=250),
            nullable=False
        )
    )
    # ### end Alembic commands ###
