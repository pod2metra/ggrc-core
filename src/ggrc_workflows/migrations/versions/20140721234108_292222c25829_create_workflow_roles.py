# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Create Workflow roles

Revision ID: 292222c25829
Revises: 1e40fcc473c1
Create Date: 2014-07-21 23:41:08.906853

"""

# revision identifiers, used by Alembic.
revision = '292222c25829'
down_revision = '1e40fcc473c1'

from alembic import op
import sqlalchemy as sa

from datetime import datetime
from sqlalchemy.sql import table, column, select, insert, and_
import json

contexts_table = table(
    'contexts',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('description', sa.Text),
    column('related_object_id', sa.Integer),
    column('related_object_type', sa.String),
    column('modified_by_id', sa.Integer),
    column('created_at', sa.DateTime),
    column('updated_at', sa.DateTime),
)

roles_table = table(
    'roles',
    column('id', sa.Integer),
    column('name', sa.String),
    column('permissions_json', sa.String),
    column('description', sa.Text),
    column('modified_by_id', sa.Integer),
    column('created_at', sa.DateTime),
    column('updated_at', sa.DateTime),
    column('context_id', sa.Integer),
    column('scope', sa.String),
)

user_roles_table = table(
    'user_roles',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('role_id', sa.Integer),
    column('person_id', sa.Integer),
)

WORKFLOW_ROLES = [
    ('WorkflowOwner', 'Workflow',
     """This role grants a user permission to edit workflow mappings and details"""
     ),
    ('WorkflowMember', 'Workflow',
     """This role grants a user permission to edit workflow mappings"""),
    ('BasicWorkflowReader', 'Workflow Implied', """ """),
    ('WorkflowBasicReader', 'Workflow Implied', """ """),
]


def upgrade():
    current_datetime = datetime.now()
    values = []
    for name, scope, description in WORKFLOW_ROLES:
        values.append(
            dict(
                name=name,
                permissions_json='CODE DECLARED ROLE',
                description=description,
                modified_by_id=1,
                created_at=current_datetime,
                updated_at=current_datetime,
                context_id=None,
                scope=scope,
            ))

    op.execute(roles_table.insert().values(values))


def downgrade():
    names = []
    for name, scope, description in WORKFLOW_ROLES:
        names.append(name)

    # Remove existing UserRole instances which reference these Role instances
    op.execute(
        user_roles_table.delete()\
            .where(user_roles_table.c.role_id.in_(
              select([roles_table.c.id]).where(roles_table.c.name.in_(names)))))

    # Remove the Role instances themselves
    op.execute(
        roles_table.delete()\
            .where(roles_table.c.name.in_(names)))
