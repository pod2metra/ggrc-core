# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Public programs are ownable.

Revision ID: 18bf74925b9
Revises: 4148ce155e54
Create Date: 2013-11-16 19:07:35.284837

"""

# revision identifiers, used by Alembic.
revision = '18bf74925b9'
down_revision = '4148ce155e54'

import json
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
)


def upgrade():
    op.execute(roles_table.update()\
        .values(
          permissions_json=json.dumps({
            "create": ["Program"],
            "read": ["Program"],
            "update": [
                {
                    "type": "Program",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                },
              ],
            "delete": [
                {
                    "type": "Program",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                },
              ],
            "view_object_page": ["__GGRC_ALL__"],
            }))\
        .where(roles_table.c.name=='ProgramCreator'))


def downgrade():
    op.execute(roles_table.update()\
        .values(
          permissions_json=json.dumps({
            "create": ["Program"],
            "view_object_page": ["__GGRC_ALL__"],
            }))\
        .where(roles_table.c.name=='ProgramCreator'))
