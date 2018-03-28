# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Fix system roles.

Revision ID: 8f33d9bd2043
Revises: 758b4012b5f
Create Date: 2013-09-20 14:12:32.846302

"""

# revision identifiers, used by Alembic.
revision = '8f33d9bd2043'
down_revision = '758b4012b5f'

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
    basic_objects_editable = [
        'Categorization',
        'Category',
        'Control',
        'ControlControl',
        'ControlSection',
        'Cycle',
        'DataAsset',
        'Directive',
        'Contract',
        'Policy',
        'Regulation',
        'DirectiveControl',
        'Document',
        'Facility',
        'Help',
        'Market',
        'Objective',
        'ObjectControl',
        'ObjectDocument',
        'ObjectObjective',
        'ObjectPerson',
        'ObjectSection',
        'Option',
        'OrgGroup',
        'PopulationSample',
        'Product',
        'ProgramControl',
        'ProgramDirective',
        'Project',
        'Relationship',
        'RelationshipType',
        'Section',
        'SectionObjective',
        'SystemOrProcess',
        'System',
        'Process',
        'SystemControl',
        'SystemSystem',
    ]

    basic_objects_readable = list(basic_objects_editable)
    basic_objects_readable.extend([
        'Person',
        'Program',
        'Role',
        #'UserRole', ?? why?
    ])

    basic_objects_creatable = list(basic_objects_editable)
    basic_objects_creatable.extend([
        'Person',
    ])

    basic_objects_updateable = list(basic_objects_editable)
    basic_objects_updateable.extend([
        'Person',
    ])

    basic_objects_deletable = list(basic_objects_editable)

    op.execute(roles_table.update()\
        .where(roles_table.c.name == 'Reader')\
        .values(permissions_json=json.dumps({
              'read':   basic_objects_readable,
              })))
    op.execute(roles_table.update()\
        .where(roles_table.c.name == 'ObjectEditor')\
        .values(permissions_json=json.dumps({
              'create': basic_objects_creatable,
              'read':   basic_objects_readable,
              'update': basic_objects_updateable,
              'delete': basic_objects_deletable,
              })))


def downgrade():
    # No reason to downgrade this one
    pass
