# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

scope = "System"
description = """
  This role grants a user the permission to create public and private programs.
  """
permissions = {
    "read": [
        "Program",
    ],
    "create": [
        "Program",
    ],
    "view_object_page": [
        "__GGRC_ALL__"
    ],
    "update": [
    ],
    "delete": [
    ]
}
