# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
""" Module for handling import and export of all workflow models """

from ggrc_workflows import models

IMPORTABLE = {
    "workflow": models.Workflow,
    "task group": models.TaskGroup,
    "task_group": models.TaskGroup,
    "taskgroup": models.TaskGroup,
    "task group task": models.TaskGroupTask,
    "task_group_task": models.TaskGroupTask,
    "taskgrouptask": models.TaskGroupTask,
    "task": models.TaskGroupTask,
}

EXPORTABLE = {
    "cycle": models.Cycle,
    "cycle_task_group": models.CycleTaskGroup,
    "cycle_task_group_object_task": models.CycleTaskGroupObjectTask,
    "cycle task group object task": models.CycleTaskGroupObjectTask,
    "cycletaskgroupobjecttask": models.CycleTaskGroupObjectTask,
    "cycle task": models.CycleTaskGroupObjectTask,
    "cycletask": models.CycleTaskGroupObjectTask,
    "cycle_task": models.CycleTaskGroupObjectTask,
}
