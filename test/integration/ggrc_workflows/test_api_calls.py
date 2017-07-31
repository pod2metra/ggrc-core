# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

import unittest

import ddt

from ggrc import db
from ggrc.models import all_models

from integration.ggrc import TestCase
from integration.ggrc.api_helper import Api
from integration.ggrc.models import factories
from integration.ggrc_workflows.models import factories as wf_factories


@ddt.ddt
class TestWorkflowsApiPost(TestCase):

  def setUp(self):
    super(TestWorkflowsApiPost, self).setUp()
    self.api = Api()

  def tearDown(self):
    pass

  def test_send_invalid_data(self):
    data = self.get_workflow_dict()
    del data["workflow"]["title"]
    del data["workflow"]["context"]
    response = self.api.post(all_models.Workflow, data)
    self.assert400(response)
    # TODO: check why response.json["message"] is empty

  def test_create_one_time_workflows(self):
    data = self.get_workflow_dict()
    response = self.api.post(all_models.Workflow, data)
    self.assertEqual(response.status_code, 201)

  def test_create_weekly_workflows(self):
    data = self.get_workflow_dict()
    data["workflow"]["frequency"] = "weekly"
    data["workflow"]["title"] = "Weekly"
    response = self.api.post(all_models.Workflow, data)
    self.assertEqual(response.status_code, 201)

  def test_create_monthly_workflows(self):
    data = self.get_workflow_dict()
    data["workflow"]["frequency"] = "monthly"
    data["workflow"]["title"] = "Monthly"
    response = self.api.post(all_models.Workflow, data)
    self.assertEqual(response.status_code, 201)

  def test_create_quarterly_workflows(self):
    data = self.get_workflow_dict()
    data["workflow"]["frequency"] = "quarterly"
    data["workflow"]["title"] = "Quarterly"
    response = self.api.post(all_models.Workflow, data)
    self.assertEqual(response.status_code, 201)

  def test_create_annually_workflows(self):
    data = self.get_workflow_dict()
    data["workflow"]["frequency"] = "annually"
    data["workflow"]["title"] = "Annually"
    response = self.api.post(all_models.Workflow, data)
    self.assertEqual(response.status_code, 201)

  def test_create_task_group(self):
    wf_data = self.get_workflow_dict()
    wf_data["workflow"]["title"] = "Create_task_group"
    wf_response = self.api.post(all_models.Workflow, wf_data)

    data = self.get_task_group_dict(wf_response.json["workflow"])

    response = self.api.post(all_models.TaskGroup, data)
    self.assertEqual(response.status_code, 201)

  # TODO: Api should be able to handle invalid data
  @unittest.skip("Not implemented.")
  def test_create_task_group_invalid_workflow_data(self):
    data = self.get_task_group_dict({"id": -1, "context": {"id": -1}})
    response = self.api.post(all_models.TaskGroup, data)
    self.assert400(response)

  @staticmethod
  def get_workflow_dict():
    data = {
        "workflow": {
            "custom_attribute_definitions": [],
            "custom_attributes": {},
            "title": "One_time",
            "description": "",
            "frequency": "one_time",
            "notify_on_change": False,
            "task_group_title": "Task Group 1",
            "notify_custom_message": "",
            "is_verification_needed": True,
            "owners": None,
            "context": None,
        }
    }
    return data

  @staticmethod
  def get_task_group_dict(workflow):
    data = {
        "task_group": {
            "custom_attribute_definitions": [],
            "custom_attributes": {},
            "_transient": {},
            "contact": {
                "id": 1,
                "href": "/api/people/1",
                "type": "Person"
            },
            "workflow": {
                "id": workflow["id"],
                "href": "/api/workflows/%d" % workflow["id"],
                "type": "Workflow"
            },
            "context": {
                "id": workflow["context"]["id"],
                "href": "/api/contexts/%d" % workflow["context"]["id"],
                "type": "Context"
            },
            "modal_title": "Create Task Group",
            "title": "Create_task_group",
            "description": "",
        }
    }
    return data

  @ddt.data(True, False)
  def test_autogen_verification_flag(self, flag):
    """Check is_verification_needed flag for activate WF action."""
    with factories.single_commit():
      workflow = wf_factories.WorkflowFactory(is_verification_needed=flag)
      group = wf_factories.TaskGroupFactory(workflow=workflow)
      wf_factories.TaskGroupTaskFactory(task_group=group)
    data = [{
        "cycle": {
            "autogenerate": True,
            "isOverdue": False,
            "workflow": {
                "id": workflow.id,
                "type": "Workflow",
            },
            "context": {
                "id": workflow.context_id,
                "type": "Context",
            },
        }
    }]
    resp = self.api.send_request(
        self.api.client.post,
        api_link="/api/cycles",
        data=data)
    cycle_id = resp.json[0][1]["cycle"]["id"]
    self.assertEqual(
        flag,
        all_models.Cycle.query.get(cycle_id).is_verification_needed)

  @ddt.data(True, False)
  def test_change_verification_flag(self, flag):
    """Check is_verification_needed flag isn't changeable."""
    with factories.single_commit():
      workflow = wf_factories.WorkflowFactory(is_verification_needed=flag)
    workflow_id = workflow.id
    resp = self.api.put(workflow, {"is_verification_needed": not flag})
    self.assert400(resp)
    self.assertEqual(
        flag,
        all_models.Workflow.query.get(workflow_id).is_verification_needed)

  @ddt.data(True, False)
  def test_not_change_vf_flag(self, flag):
    """Check is_verification_needed not change on update."""
    with factories.single_commit():
      workflow = wf_factories.WorkflowFactory(is_verification_needed=flag)
    workflow_id = workflow.id
    resp = self.api.put(workflow, {"is_verification_needed": flag})
    self.assert200(resp)
    self.assertEqual(
        flag,
        all_models.Workflow.query.get(workflow_id).is_verification_needed)

  @ddt.data(True, False, None)
  def test_create_vf_flag(self, flag):
    """Check is_verification_needed flag setup on create."""
    data = self.get_workflow_dict()
    if flag is None:
      data['workflow'].pop('is_verification_needed', None)
    else:
      data['workflow']['is_verification_needed'] = flag
    resp = self.api.post(all_models.Workflow, data)
    self.assertEqual(201, resp.status_code)
    workflow_id = resp.json['workflow']['id']
    self.assertEqual(
        flag if flag is not None else True,
        all_models.Workflow.query.get(workflow_id).is_verification_needed)


@ddt.ddt
class TestStatusApiPost(TestCase):
  """Test for api calls changes states of Cycle, Tasks and Groups."""

  def setUp(self):
    super(TestStatusApiPost, self).setUp()
    self.api = Api()
    with factories.single_commit():
      self.workflow = wf_factories.WorkflowFactory()
      self.cycle = wf_factories.CycleFactory(workflow=self.workflow)
      self.group = wf_factories.CycleTaskGroupFactory(
          cycle=self.cycle,
          context=self.cycle.workflow.context
      )
      self.task = wf_factories.CycleTaskFactory(
          cycle=self.cycle,
          cycle_task_group=self.group,
          context=self.cycle.workflow.context
      )

  def setup_cycle_state(self, is_verification_needed):
    """Setup cycle is_verification_needed state."""
    self.cycle.is_verification_needed = is_verification_needed
    db.session.add(self.cycle)
    db.session.commit()

  @ddt.data(u"Assigned",
            u"InProgress",
            u"Finished",
            u"Verified",
            u"Declined")
  def test_set_state_verified_task(self, state):
    """Check state for verification required task."""
    self.setup_cycle_state(True)
    resp = self.api.put(self.task, data={"status": state})
    task = all_models.CycleTaskGroupObjectTask.query.get(
        resp.json["cycle_task_group_object_task"]["id"]
    )
    self.assertEqual(state, task.status)

  @ddt.data((u"Assigned", True),
            (u"InProgress", True),
            (u"Finished", True),
            (u"Verified", False),
            (u"Declined", False))
  @ddt.unpack
  def test_state_non_verified_task(self, state, is_valid):
    """Check state for verification non required task."""
    self.setup_cycle_state(False)
    resp = self.api.put(self.task, data={"status": state})
    if is_valid:
      task = all_models.CycleTaskGroupObjectTask.query.get(
          resp.json["cycle_task_group_object_task"]["id"]
      )
      self.assertEqual(state, task.status)
    else:
      self.assert400(resp)

  @ddt.data(u"Assigned",
            u"InProgress",
            u"Finished",
            u"Verified")
  def test_state_verified_group(self, state):
    """Check state for verification required group."""
    self.setup_cycle_state(True)
    resp = self.api.put(self.group, data={"status": state})
    group = all_models.CycleTaskGroup.query.get(
        resp.json["cycle_task_group"]["id"]
    )
    self.assertEqual(state, group.status)

  @ddt.data((u"Assigned", True),
            (u"InProgress", True),
            (u"Finished", True),
            (u"Verified", False))
  @ddt.unpack
  def test_state_non_verified_group(self, state, is_valid):
    """Check state for verification non required group."""
    self.setup_cycle_state(False)
    resp = self.api.put(self.group, data={"status": state})
    if is_valid:
      group = all_models.CycleTaskGroup.query.get(
          resp.json["cycle_task_group"]["id"]
      )
      self.assertEqual(state, group.status)
    else:
      self.assert400(resp)

  @ddt.data(u"Assigned",
            u"InProgress",
            u"Finished",
            u"Verified")
  def test_state_verified_cycle(self, state):
    """Check state for verification required cycle."""
    self.setup_cycle_state(True)
    resp = self.api.put(self.cycle, data={"status": state})
    cycle = all_models.Cycle.query.get(resp.json["cycle"]["id"])
    self.assertEqual(state, cycle.status)

  @ddt.data((u"Assigned", True),
            (u"InProgress", True),
            (u"Finished", True),
            (u"Verified", False))
  @ddt.unpack
  def test_state_non_verified_cycle(self, state, is_valid):
    """Check state for verification non required cycle."""
    self.setup_cycle_state(False)
    resp = self.api.put(self.cycle, data={"status": state})
    if is_valid:
      cycle = all_models.Cycle.query.get(resp.json["cycle"]["id"])
      self.assertEqual(state, cycle.status)
    else:
      self.assert400(resp)

  @ddt.data(True, False)
  def test_change_is_verification(self, flag):
    """Try to change cycle is_verification_needed."""
    self.setup_cycle_state(flag)
    resp = self.api.put(self.cycle, data={"is_verification_needed": flag})
    self.assert200(resp)
    cycle = all_models.Cycle.query.get(resp.json["cycle"]["id"])
    self.assertEqual(flag, cycle.is_verification_needed)

  @ddt.data(True, False)
  def test_change_is_vf_wrong(self, flag):
    """Try to change cycle is_verification_needed not changed."""
    self.setup_cycle_state(flag)
    resp = self.api.put(self.cycle, data={"is_verification_needed": not flag})
    self.assert200(resp)
    cycle = all_models.Cycle.query.get(resp.json["cycle"]["id"])
    self.assertEqual(flag, cycle.is_verification_needed)

  @ddt.data(True, False)
  def test_change_cycle_none_flag(self, flag):
    """Try to change cycle is_verification_needed not changed
    by not sending is_verification_flag."""
    self.setup_cycle_state(flag)
    resp = self.api.put(self.cycle, not_send_fields=["is_verification_needed"])
    self.assert200(resp)
    cycle = all_models.Cycle.query.get(resp.json["cycle"]["id"])
    self.assertEqual(flag, cycle.is_verification_needed)

  @ddt.data(True, False)
  def test_change_wf_none_flag(self, flag):
    """Try to change workflow is_verification_needed not changed by
    not sending is_verification_flag."""
    db.engine.execute(
        "update workflows set is_verification_needed={} where id={}".format(
            flag, self.workflow.id
        )
    )
    resp = self.api.put(self.workflow,
                        not_send_fields=["is_verification_needed"])
    self.assert200(resp)
    workflow = all_models.Workflow.query.get(resp.json["workflow"]["id"])
    self.assertEqual(flag, workflow.is_verification_needed)

  @ddt.data((u"InProgress", True, True),
            (u"InProgress", False, True),
            (u"Declined", True, True),
            (u"Verified", True, False),
            (u"Finished", True, True),
            (u"Finished", False, False))
  @ddt.unpack
  def test_move_to_history(self, state, is_vf_needed, is_current):
    """Moved to history if state changed."""
    self.setup_cycle_state(is_vf_needed)
    resp = self.api.put(self.task, data={"status": state})
    task = all_models.CycleTaskGroupObjectTask.query.get(
        resp.json["cycle_task_group_object_task"]["id"]
    )
    self.assertEqual(is_current, task.cycle.is_current)
