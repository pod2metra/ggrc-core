# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Workflow related REST services."""

from ggrc.services.registry import service


def _get_contributed_models():
  from ggrc_workflows import models
  return [
      models.Workflow, models.WorkflowPerson, models.TaskGroup,
      models.TaskGroupTask, models.TaskGroupObject, models.Cycle,
      models.CycleTaskEntry, models.CycleTaskGroup,
      models.CycleTaskGroupObjectTask
  ]


def contributed_services():
  return [service(model_cls.__tablename__, model_cls)
          for model_cls in _get_contributed_models()]
