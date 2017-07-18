# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

scope = "Private Program Implied"
description = """
  A user with authorization to edit mapping objects related to a program. When
  a person has this role they can map and unmap objects to the Program but they
  are unable ble to edit the Program info, delete the Program, or assign roles
  for that Program.
  """
permissions = {
    "read": [
        "Document",
        "ObjectPerson",
        "ObjectSection",
        "Program",
        "Relationship",
        "UserRole",
        "Context",
    ],
    "create": [
        "Document",
        "ObjectPerson",
        "ObjectSection",
        "Relationship",
    ],
    "view_object_page": [
        "__GGRC_ALL__"
    ],
    "update": [
        "Document",
        "ObjectPerson",
        "ObjectSection",
        "Relationship"
    ],
    "delete": [
        "Document",
        "ObjectPerson",
        "ObjectSection",
        "Relationship",
    ]
}
