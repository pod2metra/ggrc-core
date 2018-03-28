# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

# pylint: disable=too-few-public-methods,missing-docstring,old-style-class
# pylint: disable=no-init

from datetime import date

import factory

from ggrc_workflows import models
from integration.ggrc.models.factories import ContextFactory
from integration.ggrc.models.factories import TitledFactory
from integration.ggrc.models.model_factory import ModelFactory


class WorkflowFactory(TitledFactory):
    class Meta:
        model = models.Workflow

    context = factory.SubFactory(ContextFactory)


class TaskGroupFactory(TitledFactory):
    class Meta:
        model = models.TaskGroup

    workflow = factory.SubFactory(WorkflowFactory)
    context = factory.LazyAttribute(lambda tg: tg.workflow.context)


class TaskGroupObjectFactory(ModelFactory):
    class Meta:
        model = models.TaskGroupObject

    task_group = factory.SubFactory(TaskGroupFactory)
    object_id = 0
    object_type = ""


class TaskGroupTaskFactory(TitledFactory):
    class Meta:
        model = models.TaskGroupTask

    task_group = factory.SubFactory(TaskGroupFactory)
    task_type = "text"
    start_date = date.today()
    end_date = date.today()
    context = factory.LazyAttribute(lambda tgt: tgt.task_group.context)


class CycleFactory(TitledFactory):
    class Meta:
        model = models.Cycle

    workflow = factory.SubFactory(WorkflowFactory)
    context = factory.LazyAttribute(lambda cycle: cycle.workflow.context)


class CycleTaskGroupFactory(TitledFactory):
    class Meta:
        model = models.CycleTaskGroup

    cycle = factory.SubFactory(CycleFactory)
    next_due_date = date(2015, 12, 4)


class CycleTaskFactory(TitledFactory):
    class Meta:
        model = models.CycleTaskGroupObjectTask

    cycle = factory.SubFactory(CycleFactory)
    cycle_task_group = factory.SubFactory(CycleTaskGroupFactory)
    task_group_task = factory.SubFactory(TaskGroupTaskFactory)
    status = "Assigned"
    task_type = "text"
    start_date = date(2015, 12, 4)
    end_date = date(2015, 12, 27)
    context = factory.LazyAttribute(lambda ct: ct.cycle.context)


class CycleTaskEntryFactory(ModelFactory):
    class Meta:
        model = models.CycleTaskEntry

    cycle = factory.SubFactory(CycleFactory)
    cycle_task_group_object_task = factory.SubFactory(CycleTaskFactory)
