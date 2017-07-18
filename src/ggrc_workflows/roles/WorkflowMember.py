# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

scope = "Workflow"
description = """
  """
permissions = {
    "read": [
        "Workflow",
        "WorkflowPerson",
        "TaskGroup",
        "TaskGroupObject",
        "TaskGroupTask",
        "Cycle",
        "CycleTaskGroup",
        "CycleTaskGroupObject",
        "CycleTaskGroupObjectTask",
        "CycleTaskEntry",
        "UserRole",
        "Context",
        "Document",
        "ObjectFile",
    ],
    "create": [
        "WorkflowPerson",
        "CycleTaskEntry",
        "Document",
        "ObjectFile",
    ],
    "update": [
        "WorkflowPerson",
        "Cycle",
        "CycleTaskGroup",
        "CycleTaskGroupObject",
        "CycleTaskGroupObjectTask",
        "CycleTaskEntry",
        "Document",
        "ObjectFile",
    ],
    "delete": [
        "WorkflowPerson",
        "CycleTaskEntry",
        "Document",
        "ObjectFile",
    ],
    "view_object_page": [
        "Workflow",
    ],
}
