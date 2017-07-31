# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

scope = "System"
description = """
  This role grants a user basic object creation and editing permission.
  """

owner_base = [
    "Categorization",
    "Category",
    "ControlCategory",
    "ObjectPerson",
    "Option",
    {
        "type": "BackgroundTask",
        "terms": {
            "property_name": "modified_by",
            "value": "$current_user"
        },
        "condition": "is"
    },
    "CustomAttributeDefinition",
    "CustomAttributeValue",
]
owner_read = owner_base + [
    "AccessControlList",
    {
        "type": "Relationship",
        "terms": {
            "property_name": "source,destination",
            "action": "read"
        },
        "condition": "relationship",
    },
    "Role",
    "UserRole",
    "Context",
    "Person",
]

owner_update = owner_base + [
    {
        "type": "Relationship",
        "terms": {
            "property_name": "source,destination",
            "action": "update"
        },
        "condition": "relationship",
    },
    {
        "type": "Comment",
        "terms": {
            "property_name": "modified_by",
            "value": "$current_user"
        },
        "condition": "is"
    },
]

permissions = {
    "read": owner_read,
    "create": [
        "Workflow"
        "Categorization",
        "Category",
        "ControlCategory",
        "ControlAssertion",
        "Control",
        "Comment",
        "DataAsset",
        "AccessGroup",
        "Directive",
        "Contract",
        "Policy",
        "Regulation",
        "Standard",
        "Document",
        "Facility",
        "Help",
        "Market",
        "Objective",
        "ObjectPerson",
        "Option",
        "OrgGroup",
        "Vendor",
        "PopulationSample",
        "Product",
        "Project",
        {
            "type": "Relationship",
            "terms": {
                "property_name": "source,destination",
                "action": "update"
            },
            "condition": "relationship",
        },
        "Section",
        "Clause",
        "SystemOrProcess",
        "System",
        "Process",
        "Program",
        "Context",
        {
            "type": "BackgroundTask",
            "terms": {
                "property_name": "modified_by",
                "value": "$current_user"
            },
            "condition": "is"
        },
    ],
    "view_object_page": owner_read,
    "update": owner_update,
    "delete": owner_update,
}
