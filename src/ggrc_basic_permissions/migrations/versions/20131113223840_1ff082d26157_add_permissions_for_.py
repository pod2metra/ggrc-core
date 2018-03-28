# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add permissions for Standard

Revision ID: 1ff082d26157
Revises: 376a7b2fbf2f
Create Date: 2013-11-13 22:38:40.531888

"""

# revision identifiers, used by Alembic.
revision = '1ff082d26157'
down_revision = '376a7b2fbf2f'

import json
from datetime import datetime

from alembic import op
import sqlalchemy as sa
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
'''
def update_role(role, spec):
    spec = dict(spec)
    spec['permissions_json'] = json.dumps(spec['permissions'])
    del spec['permissions']

    columns_for_update = []

    for column, value in spec.items():
      if spec[column] != role[column]:
        columns_for_update.append(column)

    if len(columns_for_update) > 0:
      new_values = {}
      for column in columns_for_update:
        new_values[column] = spec[column]
      new_values['updated_at'] = datetime.now()
      op.execute(roles_table.update()\
          .values(**new_values).where()


def assert_roles(roles_spec):
    # Usually, we try not to depend on existing data for migrations, but here
    # it's easier to just assert the full set of Roles.
    roles_query = roles_table.select(roles_table.c.name.in_(roles_spec.keys()))
    roles_results = op.execute(roles_query)

    for role_row in roles_results.fetchall():
      role_data = dict(zip(roles_results.keys(), role_row))
      assert_role(roles_spec[role_data['name']], role_data)
'''


def assert_roles(role_specs):
    current_timestamp = datetime.now()
    for role_name, role_spec in role_specs.items():
        spec = dict(role_spec)
        if 'permissions' in spec:
            spec['permissions_json'] = json.dumps(spec['permissions'])
            del spec['permissions']
        spec['updated_at'] = current_timestamp
        op.execute(roles_table.update()\
            .values(**spec).where(roles_table.c.name == role_name))


def upgrade():
    assert_roles(NEW_ROLES)


def downgrade():
    assert_roles(OLD_ROLES)


OLD_ROLES = {
    "AuditorReader": {
        "context_id":
        None,
        "permissions": {
            "read": [
                "Categorization", "Category", "Control", "ControlControl",
                "ControlSection", "DataAsset", "Directive", "Contract",
                "Policy", "Regulation", "DirectiveControl", "Document",
                "Facility", "Help", "Market", "Objective", "ObjectiveControl",
                "ObjectControl", "ObjectDocument", "ObjectObjective",
                "ObjectPerson", "ObjectSection", "Option", "OrgGroup",
                "PopulationSample", "Product", "ProgramControl",
                "ProgramDirective", "Project", "Relationship",
                "RelationshipType", "Section", "SectionObjective",
                "SystemOrProcess", "System", "Process", "SystemControl",
                "SystemSystem", "ObjectOwner", "Person", "Program", "Role"
            ],
            "create": [],
            "update": [],
            "delete": []
        },
        "scope":
        "System",
        "description":
        "A user with Auditor role for a program audit will also have this role in the default object context so that the auditor will have access to the objects required to perform the audit.",
        "name":
        "AuditorReader"
    },
    "ObjectEditor": {
        "context_id":
        None,
        "permissions": {
            "read": [
                "Categorization", "Category", "Control", "ControlControl",
                "ControlSection", "DataAsset", "Directive", "Contract",
                "Policy", "Regulation", "DirectiveControl", "Document",
                "Facility", "Help", "Market", "Objective", "ObjectiveControl",
                "ObjectControl", "ObjectDocument", "ObjectObjective",
                "ObjectPerson", "ObjectSection", "Option", "OrgGroup",
                "PopulationSample", "Product", "ProgramControl",
                "ProgramDirective", "Project", "Relationship",
                "RelationshipType", "Section", "SectionObjective",
                "SystemOrProcess", "System", "Process", "SystemControl",
                "SystemSystem", "ObjectOwner", "Person", "Program", "Role"
            ],
            "create": [
                "Categorization", "Category", "Control", "ControlControl",
                "ControlSection", "DataAsset", "Directive", "Contract",
                "Policy", "Regulation", "DirectiveControl", "Document",
                "Facility", "Help", "Market", "Objective", "ObjectiveControl",
                "ObjectControl", "ObjectDocument", "ObjectObjective",
                "ObjectPerson", "ObjectSection", "Option", "OrgGroup",
                "PopulationSample", "Product", "ProgramControl",
                "ProgramDirective", "Project", "Relationship",
                "RelationshipType", "Section", "SectionObjective",
                "SystemOrProcess", "System", "Process", "SystemControl",
                "SystemSystem", "Person"
            ],
            "update": [
                "Categorization", {
                    "type": "Category",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Control",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "ControlControl", "ControlSection", {
                    "type": "DataAsset",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Directive",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Contract",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Policy",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Regulation",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "DirectiveControl", {
                    "type": "Document",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Facility",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Help",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Market",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Objective",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "ObjectiveControl", "ObjectControl", "ObjectDocument",
                "ObjectObjective", "ObjectPerson", "ObjectSection", {
                    "type": "Option",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "OrgGroup",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "PopulationSample", {
                    "type": "Product",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "ProgramControl", "ProgramDirective", {
                    "type": "Project",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "Relationship", "RelationshipType", {
                    "type": "Section",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "SectionObjective", {
                    "type": "SystemOrProcess",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "System",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Process",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "SystemControl", "SystemSystem", "Person"
            ],
            "delete": [
                "Categorization", {
                    "type": "Category",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Control",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "ControlControl", "ControlSection", {
                    "type": "DataAsset",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Directive",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Contract",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Policy",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Regulation",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "DirectiveControl", {
                    "type": "Document",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Facility",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Help",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Market",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Objective",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "ObjectiveControl", "ObjectControl", "ObjectDocument",
                "ObjectObjective", "ObjectPerson", "ObjectSection", {
                    "type": "Option",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "OrgGroup",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "PopulationSample", {
                    "type": "Product",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "ProgramControl", "ProgramDirective", {
                    "type": "Project",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "Relationship", "RelationshipType", {
                    "type": "Section",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "SectionObjective", {
                    "type": "SystemOrProcess",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "System",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Process",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "SystemControl", "SystemSystem"
            ]
        },
        "scope":
        "System",
        "description":
        "This role grants a user basic object creation and editing permission.",
        "name":
        "ObjectEditor"
    },
    "Reader": {
        "context_id":
        None,
        "permissions": {
            "read": [
                "Categorization", "Category", "Control", "ControlControl",
                "ControlSection", "DataAsset", "Directive", "Contract",
                "Policy", "Regulation", "DirectiveControl", "Document",
                "Facility", "Help", "Market", "Objective", "ObjectiveControl",
                "ObjectControl", "ObjectDocument", "ObjectObjective",
                "ObjectPerson", "ObjectSection", "Option", "OrgGroup",
                "PopulationSample", "Product", "ProgramControl",
                "ProgramDirective", "Project", "Relationship",
                "RelationshipType", "Section", "SectionObjective",
                "SystemOrProcess", "System", "Process", "SystemControl",
                "SystemSystem", "ObjectOwner", "Person", "Program", "Role"
            ],
            "create": [],
            "update": [],
            "delete": []
        },
        "scope":
        "System",
        "description":
        "This role grants a user basic, read-only, access permission to a gGRC instance.",
        "name":
        "Reader"
    },
}

NEW_ROLES = {
    "AuditorReader": {
        "context_id":
        None,
        "permissions": {
            "read": [
                "Categorization", "Category", "Control", "ControlControl",
                "ControlSection", "DataAsset", "Directive", "Contract",
                "Policy", "Regulation", "Standard", "DirectiveControl",
                "Document", "Facility", "Help", "Market", "Objective",
                "ObjectiveControl", "ObjectControl", "ObjectDocument",
                "ObjectObjective", "ObjectPerson", "ObjectSection", "Option",
                "OrgGroup", "PopulationSample", "Product", "ProgramControl",
                "ProgramDirective", "Project", "Relationship",
                "RelationshipType", "Section", "SectionObjective",
                "SystemOrProcess", "System", "Process", "SystemControl",
                "SystemSystem", "ObjectOwner", "Person", "Program", "Role"
            ],
            "create": [],
            "update": [],
            "delete": []
        },
        "scope":
        "System",
        "description":
        "A user with Auditor role for a program audit will also have this role in the default object context so that the auditor will have access to the objects required to perform the audit.",
        "name":
        "AuditorReader"
    },
    "ObjectEditor": {
        "context_id":
        None,
        "permissions": {
            "read": [
                "Categorization", "Category", "Control", "ControlControl",
                "ControlSection", "DataAsset", "Directive", "Contract",
                "Policy", "Regulation", "Standard", "DirectiveControl",
                "Document", "Facility", "Help", "Market", "Objective",
                "ObjectiveControl", "ObjectControl", "ObjectDocument",
                "ObjectObjective", "ObjectPerson", "ObjectSection", "Option",
                "OrgGroup", "PopulationSample", "Product", "ProgramControl",
                "ProgramDirective", "Project", "Relationship",
                "RelationshipType", "Section", "SectionObjective",
                "SystemOrProcess", "System", "Process", "SystemControl",
                "SystemSystem", "ObjectOwner", "Person", "Program", "Role"
            ],
            "create": [
                "Categorization", "Category", "Control", "ControlControl",
                "ControlSection", "DataAsset", "Directive", "Contract",
                "Policy", "Regulation", "Standard", "DirectiveControl",
                "Document", "Facility", "Help", "Market", "Objective",
                "ObjectiveControl", "ObjectControl", "ObjectDocument",
                "ObjectObjective", "ObjectPerson", "ObjectSection", "Option",
                "OrgGroup", "PopulationSample", "Product", "ProgramControl",
                "ProgramDirective", "Project", "Relationship",
                "RelationshipType", "Section", "SectionObjective",
                "SystemOrProcess", "System", "Process", "SystemControl",
                "SystemSystem", "Person"
            ],
            "update": [
                "Categorization", {
                    "type": "Category",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Control",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "ControlControl", "ControlSection", {
                    "type": "DataAsset",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Directive",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Contract",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Policy",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Regulation",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Standard",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "DirectiveControl", {
                    "type": "Document",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Facility",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Help",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Market",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Objective",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "ObjectiveControl", "ObjectControl", "ObjectDocument",
                "ObjectObjective", "ObjectPerson", "ObjectSection", {
                    "type": "Option",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "OrgGroup",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "PopulationSample", {
                    "type": "Product",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "ProgramControl", "ProgramDirective", {
                    "type": "Project",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "Relationship", "RelationshipType", {
                    "type": "Section",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "SectionObjective", {
                    "type": "SystemOrProcess",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "System",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Process",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "SystemControl", "SystemSystem", "Person"
            ],
            "delete": [
                "Categorization", {
                    "type": "Category",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Control",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "ControlControl", "ControlSection", {
                    "type": "DataAsset",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Directive",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Contract",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Policy",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Regulation",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Standard",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "DirectiveControl", {
                    "type": "Document",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Facility",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Help",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Market",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Objective",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "ObjectiveControl", "ObjectControl", "ObjectDocument",
                "ObjectObjective", "ObjectPerson", "ObjectSection", {
                    "type": "Option",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "OrgGroup",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "PopulationSample", {
                    "type": "Product",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "ProgramControl", "ProgramDirective", {
                    "type": "Project",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "Relationship", "RelationshipType", {
                    "type": "Section",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "SectionObjective", {
                    "type": "SystemOrProcess",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "System",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, {
                    "type": "Process",
                    "terms": {
                        "list_property": "owners",
                        "value": "$current_user"
                    },
                    "condition": "contains"
                }, "SystemControl", "SystemSystem"
            ]
        },
        "scope":
        "System",
        "description":
        "This role grants a user basic object creation and editing permission.",
        "name":
        "ObjectEditor"
    },
    "Reader": {
        "context_id":
        None,
        "permissions": {
            "read": [
                "Categorization", "Category", "Control", "ControlControl",
                "ControlSection", "DataAsset", "Directive", "Contract",
                "Policy", "Regulation", "Standard", "DirectiveControl",
                "Document", "Facility", "Help", "Market", "Objective",
                "ObjectiveControl", "ObjectControl", "ObjectDocument",
                "ObjectObjective", "ObjectPerson", "ObjectSection", "Option",
                "OrgGroup", "PopulationSample", "Product", "ProgramControl",
                "ProgramDirective", "Project", "Relationship",
                "RelationshipType", "Section", "SectionObjective",
                "SystemOrProcess", "System", "Process", "SystemControl",
                "SystemSystem", "ObjectOwner", "Person", "Program", "Role"
            ],
            "create": [],
            "update": [],
            "delete": []
        },
        "scope":
        "System",
        "description":
        "This role grants a user basic, read-only, access permission to a gGRC instance.",
        "name":
        "Reader"
    },
}
