# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Workflow related generators
"""
import copy

from datetime import date

from ggrc import db
from ggrc import builder
from ggrc.access_control import role
from ggrc_workflows.models import Cycle
from ggrc_workflows.models import TaskGroup
from ggrc_workflows.models import TaskGroupObject
from ggrc_workflows.models import TaskGroupTask
from ggrc_workflows.models import Workflow
from integration.ggrc.generator import Generator
from integration.ggrc.models import factories


class WorkflowsGenerator(Generator):

  def generate_workflow(self, data=None):
    """ create a workflow with dict data
    return: wf if it was created, or response otherwise
    """
    if data is None:
      data = {}
    obj_name = "workflow"
    data = copy.deepcopy(data)

    tgs = data.pop("task_groups", [])

    wf = Workflow(title="wf " + factories.random_str())
    obj_dict = self.obj_to_dict(wf, obj_name)
    obj_dict[obj_name].update(data)

    response, workflow = self.generate(Workflow, obj_name, obj_dict)

    for tg in tgs:
      self.generate_task_group(workflow, tg)

    return response, workflow

  def generate_task_group(self, workflow=None, data=None):
    if data is None:
      data = {}
    if not workflow:
      _, workflow = self.generate_workflow()
    data = copy.deepcopy(data)

    tgts = data.pop("task_group_tasks", [])
    tgos = data.pop("task_group_objects", [])

    obj_name = "task_group"
    workflow = self._session_add(workflow)

    tg = TaskGroup(
        title="tg " + factories.random_str(),
        workflow_id=workflow.id,
        context_id=workflow.context.id,
        contact_id=1
    )
    obj_dict = self.obj_to_dict(tg, obj_name)
    obj_dict[obj_name].update(data)

    response, task_group = self.generate(TaskGroup, obj_name, obj_dict)

    for tgt in tgts:
      self.generate_task_group_task(task_group, tgt)
    for tgo in tgos:
      self.generate_task_group_object(task_group, tgo)

    return response, task_group

  def generate_task_group_task(self, task_group=None, data=None):
    if data is None:
      data = {}
    if not task_group:
      _, task_group = self.generate_task_group()
    task_group = self._session_add(task_group)

    default_start = self.random_date()
    default_end = self.random_date(default_start, date.today())
    obj_name = "task_group_task"
    cycle_task_role_id = {
        v: k for (k, v) in
        role.get_custom_roles_for("TaskGroupTask").iteritems()
    }['Task Assignee']
    tgt = TaskGroupTask(
        task_group_id=task_group.id,
        context_id=task_group.context.id,
        title="tgt " + factories.random_str(),
        start_date=default_start,
        end_date=default_end,
    )
    obj_dict = self.obj_to_dict(tgt, obj_name)
    if "access_control_list" not in data:
      data["access_control_list"] = [{
          "ac_role_id": cycle_task_role_id,
          "person": {"id": 1},
      }]
    obj_dict[obj_name].update(data)
    return self.generate(TaskGroupTask, obj_name, obj_dict)

  def generate_task_group_object(self, task_group=None, obj=None):
    if not task_group:
      _, task_group = self.generate_task_group()
    task_group = self._session_add(task_group)
    obj = self._session_add(obj)

    obj_name = "task_group_object"

    tgo = TaskGroupObject(
        object_id=obj.id,
        object=obj,
        task_group_id=task_group.id,
        context_id=task_group.context.id
    )
    obj_dict = self.obj_to_dict(tgo, obj_name)

    return self.generate(TaskGroupObject, obj_name, obj_dict)

  def generate_cycle(self, workflow=None):
    if not workflow:
      _, workflow = self.generate_workflow()

    workflow = self._session_add(workflow)  # this should be nicer

    obj_name = "cycle"

    obj_dict = {
        obj_name: {
            "workflow": {
                "id": workflow.id,
                "type": workflow.__class__.__name__,
                "href": "/api/workflows/%d" % workflow.id
            },
            "context": {
                "id": workflow.context.id,
                "type": workflow.context.__class__.__name__,
                "href": "/api/workflows/%d" % workflow.context.id
            },
            "autogenerate": "true"
        }
    }

    return self.generate(Cycle, obj_name, obj_dict)

  def activate_workflow(self, workflow):
    workflow = self._session_add(workflow)
    return self.modify_workflow(workflow, {
        "status": "Active",
        "recurrences": bool(workflow.repeat_every and workflow.unit)
    })

  def modify_workflow(self, wf=None, data=None):
    if data is None:
      data = {}
    if not wf:
      _, wf = self.generate_workflow()
    wf = self._session_add(wf)

    obj_name = "workflow"

    obj_dict = builder.json.publish(wf)
    builder.json.publish_representation(obj_dict)
    obj_dict.update(data)

    default = {obj_name: obj_dict}

    response, workflow = self.modify(wf, obj_name, default)

    return response, workflow

  def modify_object(self, obj, data=None):
    if data is None:
      data = {}
    obj = self._session_add(obj)

    obj_name = obj._inflector.table_singular

    obj_dict = builder.json.publish(obj)
    builder.json.publish_representation(obj_dict)
    obj_dict.update(data)

    obj_data = {obj_name: obj_dict}

    response, generated_object = self.modify(obj, obj_name, obj_data)

    return response, generated_object

  def _session_add(self, obj):
    """ Sometimes tests throw conflicting state present error."""
    try:
      db.session.add(obj)
      return obj
    except:
      return obj.__class__.query.get(obj.id)
