# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add roles and role implications for gdrive connectors

Revision ID: 24c56d737c18
Revises: 18bf74925b9
Create Date: 2013-11-22 00:10:39.635553

"""

# revision identifiers, used by Alembic.
revision = '24c56d737c18'
down_revision = '18bf74925b9'

import sqlalchemy as sa
from alembic import op
from datetime import datetime
from sqlalchemy.sql import table, column, select
import json

roles_table = table('roles', column('id', sa.Integer), column(
    'name', sa.String), column('permissions_json', sa.String))


def upgrade():
    folder_set = set(["Program", "Audit", "Request"])

    connection = op.get_bind()
    roles = connection.execute(
        select([roles_table.c.id, roles_table.c.permissions_json]))

    for role_id, permissions_json in roles:
        permissions = json.loads(permissions_json)
        if (permissions is None):
            continue

        for ptype in ["read", "create", "delete"]:
            if (ptype in permissions and any(
                    # filter out "terms" objects
                    set([
                        i
                        if type(i) == str or type(i) == unicode else i["type"]
                        for i in permissions[ptype]
                    ]).intersection(folder_set))
                    and "ObjectFolder" not in permissions[ptype]):
                permissions[ptype].append("ObjectFolder")
            if (ptype in permissions and "Document" in permissions[ptype]
                    and "ObjectFile" not in permissions[ptype]):
                permissions[ptype].append("ObjectFile")
            if (ptype in permissions and "Meeting" in permissions[ptype]
                    and "ObjectEvent" not in permissions[ptype]):
                permissions[ptype].append("ObjectEvent")

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

        for ptype in ["read", "create", "delete"]:
            if (ptype in permissions):
                permissions[ptype] = [i for i in permissions[ptype] \
                    if i not in ["ObjectFolder", "ObjectFile", "ObjectEvent"]]

        op.execute(roles_table.update().values(permissions_json = json.dumps(permissions))\
                .where(roles_table.c.id == role_id))
