# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add meetings to permissions

Revision ID: 13b49798db19
Revises: 24c56d737c18
Create Date: 2013-11-26 00:30:26.022227

"""

# revision identifiers, used by Alembic.
revision = '13b49798db19'
down_revision = '24c56d737c18'

import sqlalchemy as sa
from alembic import op
from datetime import datetime
from sqlalchemy.sql import table, column, select
import json

roles_table = table('roles', column('id', sa.Integer), column(
    'name', sa.String), column('permissions_json', sa.String))


def upgrade():
    meeting_set = set(["InterviewResponse"])

    connection = op.get_bind()
    roles = connection.execute(
        select([roles_table.c.id, roles_table.c.permissions_json]))

    for role_id, permissions_json in roles:
        permissions = json.loads(permissions_json)
        if (permissions is None):
            continue

        for ptype in ["read", "create", "delete", "update"]:
            if (ptype in permissions and any(
                    # filter out "terms" objects
                    set([
                        i
                        if type(i) == str or type(i) == unicode else i["type"]
                        for i in permissions[ptype]
                    ]).intersection(meeting_set))
                    and "Meeting" not in permissions[ptype]):
                permissions[ptype].append("Meeting")

        op.execute(roles_table.update().values(permissions_json = json.dumps(permissions))\
                .where(roles_table.c.id == role_id))


def downgrade():
    connection = op.get_bind()
    roles = connection.execute(
        select([roles_table.c.id, roles_table.c.permissions_json]))

    for role_id, permissions_json in roles:
        permissions = json.loads(permissions_json)
        if (permissions is None):
            continue

        for ptype in ["read", "create", "delete", "update"]:
            if (ptype in permissions):
                permissions[ptype] = [i for i in permissions[ptype] \
                    if i not in ["Meeting"]]

        op.execute(roles_table.update().values(permissions_json = json.dumps(permissions))\
                .where(roles_table.c.id == role_id))
