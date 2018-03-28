# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Hide the AuditorReader role by changing its scope.

Revision ID: 37b63b122038
Revises: 1ff082d26157
Create Date: 2013-11-08 22:48:46.956836

"""

# revision identifiers, used by Alembic.
revision = '37b63b122038'
down_revision = '1ff082d26157'

import sqlalchemy as sa
from alembic import op
from datetime import datetime
from sqlalchemy.sql import table, column

roles_table = table(
    'roles',
    column('id', sa.Integer),
    column('name', sa.String),
    column('permissions_json', sa.Text),
    column('description', sa.Text),
    column('modified_by_id', sa.Integer),
    column('created_at', sa.DateTime),
    column('updated_at', sa.DateTime),
    column('context_id', sa.Integer),
    column('scope', sa.String),
)


def upgrade():
    op.execute(
        roles_table.update()\
            .where(roles_table.c.name == 'AuditorReader')\
            .values({'scope': 'System Implied'})
            )


def downgrade():
    op.execute(
      roles_table.update()\
          .where(roles_table.c.name == 'AuditorReader')\
          .values({'scope': 'System'})
          )
