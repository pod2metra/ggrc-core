# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Tests for api calls on ggrc_workflows module."""

import datetime
import unittest
import collections
from mock import MagicMock

import ddt
import freezegun
import sqlalchemy as sa

from ggrc import db
from ggrc.models import all_models
from ggrc.fulltext import mysql

from integration.ggrc import TestCase
from integration.ggrc.api_helper import Api
from integration.ggrc import generator
from integration.ggrc.models import factories
from integration.ggrc_workflows import generator as wf_generator
from integration.ggrc_workflows import WorkflowTestCase
from integration.ggrc_workflows.models import factories as wf_factories


@ddt.ddt  # pylint: disable=too-many-public-methods
class TestWorkflowsApiPost(TestCase):
  """Test class for ggrc workflow api post action."""

  def setUp(self):
    super(TestWorkflowsApiPost, self).setUp()
    self.api = Api()
    self.generator = wf_generator.WorkflowsGenerator()

  def tearDown(self):
    pass

  def test_send_invalid_data(self):
    """Test send invalid data on Workflow post."""
    data = self.get_workflow_dict()
    del data["workflow"]["title"]
    del data["workflow"]["context"]
    response = self.api.post(all_models.Workflow, data)
    self.assert400(response)
    # TODO: check why response.json["message"] is empty

  def test_create_one_time_workflows(self):
    """Test simple create one time Workflow over api."""
    data = self.get_workflow_dict()
    response = self.api.post(all_models.Workflow, data)
    self.assertEqual(response.status_code, 201)

  def test_create_weekly_workflow(self):
    """Test create valid weekly wf"""
    data = self.get_workflow_dict()
    data["workflow"]["repeat_every"] = 7
    data["workflow"]["unit"] = "day"
    data["workflow"]["title"] = "Weekly"
    response = self.api.post(all_models.Workflow, data)
    self.assertEqual(response.status_code, 201)

  def test_create_annually_workflow(self):
    """Test create valid annual wf"""
    data = self.get_workflow_dict()
    data["workflow"]["repeat_every"] = 12
    data["workflow"]["unit"] = "month"
    data["workflow"]["title"] = "Annually"
    response = self.api.post(all_models.Workflow, data)
    self.assertEqual(response.status_code, 201)

  @ddt.data("wrong value", 0, -4)
  def test_create_wrong_repeat_every_workflow(self, value):  # noqa pylint: disable=invalid-name
    """Test case for invalid repeat_every value"""
    data = self.get_workflow_dict()
    data["workflow"]["repeat_every"] = value
    data["workflow"]["unit"] = "month"
    data["workflow"]["title"] = "Wrong wf"
    response = self.api.post(all_models.Workflow, data)
    self.assertEqual(response.status_code, 400)

  def test_create_wrong_unit_workflow(self):
    """Test case for invalid unit value"""
    data = self.get_workflow_dict()
    data["workflow"]["repeat_every"] = 12
    data["workflow"]["unit"] = "wrong value"
    data["workflow"]["title"] = "Wrong wf"
    response = self.api.post(all_models.Workflow, data)
    self.assertEqual(response.status_code, 400)

  def test_create_task_group(self):
    """Test create task group over api."""
    wf_data = self.get_workflow_dict()
    wf_data["workflow"]["title"] = "Create_task_group"
    wf_response = self.api.post(all_models.Workflow, wf_data)

    data = self.get_task_group_dict(wf_response.json["workflow"])

    response = self.api.post(all_models.TaskGroup, data)
    self.assertEqual(response.status_code, 201)

  # TODO: Api should be able to handle invalid data
  @unittest.skip("Not implemented.")
  def test_create_task_group_invalid_workflow_data(self):  # noqa pylint: disable=invalid-name
    """Test create task group with invalid data."""
    data = self.get_task_group_dict({"id": -1, "context": {"id": -1}})
    response = self.api.post(all_models.TaskGroup, data)
    self.assert400(response)

  @staticmethod
  def get_workflow_dict():
    return {
        "workflow": {
            "custom_attribute_definitions": [],
            "custom_attributes": {},
            "title": "One_time",
            "description": "",
            "unit": None,
            "repeat_every": None,
            "notify_on_change": False,
            "task_group_title": "Task Group 1",
            "notify_custom_message": "",
            "is_verification_needed": True,
            "owners": None,
            "context": None,
        }
    }

  @staticmethod
  def get_task_group_dict(workflow):
    return {
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

  @ddt.data({},
            {"repeat_every": 5,
             "unit": "month"})
  def test_repeat_multiplier_field(self, data):
    """Check repeat_multiplier is set to 0 after wf creation."""
    with factories.single_commit():
      workflow = wf_factories.WorkflowFactory(**data)
    workflow_id = workflow.id
    self.assertEqual(
        0,
        all_models.Workflow.query.get(workflow_id).repeat_multiplier
    )

  # TODO: Unskip in the patch 2
  @unittest.skip("Will be activated in patch 2")
  def test_change_to_one_time_wf(self):
    """Check repeat_every and unit can be set to Null only together."""
    with factories.single_commit():
      workflow = wf_factories.WorkflowFactory(repeat_every=12,
                                              unit="day")
    resp = self.api.put(workflow, {"repeat_every": None,
                                   "unit": None})
    self.assert200(resp)

  @ddt.data({"repeat_every": 5},
            {"unit": "month"})
  def test_change_repeat_every(self, data):
    """Check repeat_every or unit can not be changed once set."""
    with factories.single_commit():
      workflow = wf_factories.WorkflowFactory()
    resp = self.api.put(workflow, data)
    self.assert400(resp)

  def test_not_change_to_one_time_wf(self):
    """Check repeat_every or unit can't be set to Null separately.
    This test will be useful in the 2nd patch, where we allow to change
    WF setup
    """
    with factories.single_commit():
      workflow = wf_factories.WorkflowFactory(repeat_every=12,
                                              unit="day")
    resp = self.api.put(workflow, {"repeat_every": None})
    self.assert400(resp)
    resp = self.api.put(workflow, {"unit": None})
    self.assert400(resp)

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
  def test_change_verification_flag_positive(self, flag):  # noqa pylint: disable=invalid-name
    """is_verification_needed flag is changeable for DRAFT workflow."""
    with factories.single_commit():
      workflow = wf_factories.WorkflowFactory(is_verification_needed=flag)
    self.assertEqual(workflow.status, all_models.Workflow.DRAFT)
    workflow_id = workflow.id
    resp = self.api.put(workflow, {"is_verification_needed": not flag})
    self.assert200(resp)
    self.assertEqual(
        all_models.Workflow.query.get(workflow_id).is_verification_needed,
        not flag)

  @ddt.data(True, False)
  def test_change_verification_flag_negative(self, flag):  # noqa pylint: disable=invalid-name
    with freezegun.freeze_time("2017-08-10"):
      with factories.single_commit():
        workflow = wf_factories.WorkflowFactory(
            unit=all_models.Workflow.WEEK_UNIT,
            is_verification_needed=flag,
            repeat_every=1)
        wf_factories.TaskGroupTaskFactory(
            task_group=wf_factories.TaskGroupFactory(
                context=factories.ContextFactory(),
                workflow=workflow
            ),
            # Two cycles should be created
            start_date=datetime.date(2017, 8, 3),
            end_date=datetime.date(2017, 8, 7))
      workflow_id = workflow.id
      self.assertEqual(workflow.status, all_models.Workflow.DRAFT)
      self.generator.activate_workflow(workflow)
      workflow = all_models.Workflow.query.get(workflow_id)
      self.assertEqual(workflow.status, all_models.Workflow.ACTIVE)
      resp = self.api.put(workflow, {"is_verification_needed": not flag})
      self.assert400(resp)
      workflow = all_models.Workflow.query.get(workflow_id)
      self.assertEqual(workflow.is_verification_needed, flag)

      # End all current cycles
      for cycle in workflow.cycles:
        self.generator.modify_object(cycle, {'is_current': False})
      workflow = all_models.Workflow.query.filter(
          all_models.Workflow.id == workflow_id).first()
      self.assertEqual(workflow.status, all_models.Workflow.INACTIVE)
      resp = self.api.put(workflow, {"is_verification_needed": not flag})
      self.assert400(resp)
      workflow = all_models.Workflow.query.get(workflow_id)
      self.assertEqual(workflow.is_verification_needed, flag)

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


class TestTaskGroupTaskApiPost(WorkflowTestCase):
  """
  Tesk TestTaskGroupTask basic api actions
  """
  def test_create_tgt_correct_dates(self):
    """Test case for correct tgt start_ end_ dates"""
    response, _ = self.generator.generate_task_group_task(
        data={"start_date": datetime.date.today(),
              "end_date": datetime.date.today() + datetime.timedelta(days=4)}
    )
    self.assertEqual(response.status_code, 201)

  def test_create_tgt_wrong_dates(self):
    """Test case for tgt wrong start_ end_ dates"""
    with self.assertRaises(Exception):
      self.generator.generate_task_group_task(
          data={
              "start_date": datetime.date.today(),
              "end_date": datetime.date.today() - datetime.timedelta(days=4)
          }
      )

  def test_tgt_has_view_dates(self):
    """Test get view only fields for TGT."""
    workflow = wf_factories.WorkflowFactory()
    task_group = wf_factories.TaskGroupFactory(workflow=workflow)
    tgt = wf_factories.TaskGroupTaskFactory(task_group=task_group)
    resp = self.api.get(tgt, tgt.id)
    self.assertIn("task_group_task", resp.json)
    self.assertIn("view_start_date", resp.json["task_group_task"])
    self.assertIn("view_end_date", resp.json["task_group_task"])


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


@ddt.ddt
class TestCloneWorkflow(TestCase):
  """Test clone Workflow operation."""

  def setUp(self):
    super(TestCloneWorkflow, self).setUp()
    self.object_generator = generator.ObjectGenerator()

  @ddt.data(
      (None, None),
      (all_models.Workflow.DAY_UNIT, 10),
      (all_models.Workflow.MONTH_UNIT, 10),
      (all_models.Workflow.WEEK_UNIT, 10),
  )
  @ddt.unpack
  def test_workflow_copy(self, unit, repeat_every):
    """Check clone wf with unit and repeat."""
    with factories.single_commit():
      workflow = wf_factories.WorkflowFactory(unit=unit,
                                              repeat_every=repeat_every)
    _, clone_wf = self.object_generator.generate_object(
        all_models.Workflow, {"title": "WF - copy 1", "clone": workflow.id})
    self.assertEqual(unit, clone_wf.unit)
    self.assertEqual(repeat_every, clone_wf.repeat_every)


@ddt.ddt
class TestStatusApiPatch(TestCase):
  """Test CycleTask's statuses change via PATCH operation."""
  ASSIGNED = all_models.CycleTaskGroupObjectTask.ASSIGNED
  IN_PROGRESS = all_models.CycleTaskGroupObjectTask.IN_PROGRESS
  FINISHED = all_models.CycleTaskGroupObjectTask.FINISHED
  DEPRECATED = all_models.CycleTaskGroupObjectTask.DEPRECATED
  VERIFIED = all_models.CycleTaskGroupObjectTask.VERIFIED
  DECLINED = all_models.CycleTaskGroupObjectTask.DECLINED

  @staticmethod
  def _create_cycle_structure():
    """Create cycle structure.

    It will create workflow, cycle, group and 3 tasks in that group.

    Retruns tuple:
        workflow, cycle, group and list of tasks.
    """
    workflow = wf_factories.WorkflowFactory(
        status=all_models.Workflow.ACTIVE)
    cycle = wf_factories.CycleFactory(workflow=workflow)
    group = wf_factories.CycleTaskGroupFactory(
        cycle=cycle,
        context=cycle.workflow.context
    )
    tasks = []
    for ind in xrange(3):
      tasks.append(wf_factories.CycleTaskFactory(
          title='task{}'.format(ind),
          cycle=cycle,
          cycle_task_group=group,
          context=cycle.workflow.context,
          start_date=datetime.datetime.now(),
          end_date=datetime.datetime.now() + datetime.timedelta(7)
      ))
    return workflow, cycle, group, tasks

  def setUp(self):
    super(TestStatusApiPatch, self).setUp()
    self.api = Api()

    with factories.single_commit():
      self.assignee = factories.PersonFactory(email="assignee@example.com")
      (
          self.workflow,
          self.cycle,
          self.group,
          self.tasks,
      ) = self._create_cycle_structure()
    self.group_id = self.group.id
    # Emulate that current user is assignee for all test CycleTasks.
    all_models.CycleTaskGroupObjectTask.current_user_wfo_or_assignee = (
        MagicMock(return_value=True))

  def _update_ct_via_patch(self, new_states):
    """Update CycleTasks' state via PATCH.

    Args:
        new_states: List of states to which CTs should be moved via PATCH.

    Returns:
        JSON response which was returned by back-end.
    """
    data = [{"state": state, "id": self.tasks[ind].id}
            for ind, state in enumerate(new_states)]
    resp = self.api.patch(all_models.CycleTaskGroupObjectTask, data)
    return resp.json

  def _get_exp_response(self, exp_res):
    """Format expected response from CycleTasks' test data indexes.

    Args:
        exp_res: Expected results dict: {test_ctask_index: response_status}

    Returns:
        [{'id': updated_task_id, 'status': 'success|skipped|error'}, ...]
    """
    return [{'id': self.tasks[ind].id, 'status': status}
            for ind, status in exp_res.iteritems()]

  @ddt.data(
      (
          # New statuses which we try to set during the test
          [IN_PROGRESS, IN_PROGRESS, IN_PROGRESS],
          # Expected results: {test_ctask_index: response_status}
          {0: 'updated', 1: 'updated', 2: 'updated'},
          # Expected states after update
          [IN_PROGRESS, IN_PROGRESS, IN_PROGRESS]
      ),
      (
          [DEPRECATED, DEPRECATED, DEPRECATED],
          {0: 'updated', 1: 'updated', 2: 'updated'},
          [DEPRECATED, DEPRECATED, DEPRECATED]
      ),
      (
          [FINISHED, FINISHED, FINISHED],
          {0: 'skipped', 1: 'skipped', 2: 'skipped'},
          [ASSIGNED, ASSIGNED, ASSIGNED]
      )
  )
  @ddt.unpack
  def test_ct_status_bulk_update_ok(self, new_states, exp_res, exp_states):
    """Check CycleTasks' state update with valid data via PATCH."""
    self.assertItemsEqual(self._get_exp_response(exp_res),
                          self._update_ct_via_patch(new_states))
    self.assertItemsEqual(
        exp_states,
        [obj.status for obj in all_models.CycleTaskGroupObjectTask.query])

  def test_ct_status_bulk_update_json_error(self):  # noqa pylint: disable=invalid-name
    """Check CycleTasks' state update with invalid data via PATCH."""
    exp_resp = {
        "message": "Request's JSON contains multiple statuses for CycleTasks",
        "code": 400
    }
    self.assertEqual(exp_resp, self._update_ct_via_patch([self.IN_PROGRESS,
                                                          self.FINISHED,
                                                          self.IN_PROGRESS]))
    self.assertItemsEqual(
        [self.ASSIGNED, self.ASSIGNED, self.ASSIGNED],
        [obj.status for obj in all_models.CycleTaskGroupObjectTask.query])

  def test_ct_status_bulk_update_without_permissions(self):  # noqa pylint: disable=invalid-name
    """Check CycleTasks' state update without permissions via PATCH."""
    # Emulate that current user is not assignee for all test CycleTasks.
    all_models.CycleTaskGroupObjectTask.current_user_wfo_or_assignee = (
        MagicMock(return_value=False))
    self.assertItemsEqual(
        self._get_exp_response({0: 'skipped', 1: 'skipped', 2: 'skipped'}),
        self._update_ct_via_patch([self.IN_PROGRESS,
                                   self.IN_PROGRESS,
                                   self.IN_PROGRESS]))
    self.assertItemsEqual(
        [self.ASSIGNED, self.ASSIGNED, self.ASSIGNED],
        [obj.status for obj in all_models.CycleTaskGroupObjectTask.query])

  def test_ct_status_bulk_update_invalid_state(self):  # noqa pylint: disable=invalid-name
    """Check CycleTasks' state update with invalid statuses via PATCH."""
    exp_resp = {
        "message": "Request's JSON contains invalid statuses for CycleTasks",
        "code": 400
    }
    self.assertItemsEqual(exp_resp,
                          self._update_ct_via_patch(['InVaLiD', 'InVaLiD']))
    self.assertItemsEqual(
        [self.ASSIGNED, self.ASSIGNED, self.ASSIGNED],
        [obj.status for obj in all_models.CycleTaskGroupObjectTask.query])

  def refresh_set_up_instances(self):
    """Update set up instances after request operation."""
    self.tasks = all_models.CycleTaskGroupObjectTask.query.order_by(
        all_models.CycleTaskGroupObjectTask.id
    ).all()
    self.group = all_models.CycleTaskGroup.query.get(self.group_id)
    self.cycle = self.group.cycle
    self.workflow = self.group.cycle.workflow

  def assert_notifications_for_object(self, obj, *expected_notification_list):
    """Assert object notifications are equal to expected notification list."""
    active_notifications = all_models.Notification.query.filter(
        all_models.Notification.object_id == obj.id,
        all_models.Notification.object_type == obj.type,
        sa.or_(all_models.Notification.sent_at.is_(None),
               all_models.Notification.repeating == sa.true())
    ).all()
    self.assertEqual(
        sorted(expected_notification_list),
        sorted([n.notification_type.name for n in active_notifications])
    )

  def assert_latest_revision_status(self, *obj_status_chain):
    """Assert last status for object and status chain."""
    objs_status_dict = {(o.type, o.id): s for o, s in obj_status_chain}
    revisions = []
    for o_type, o_id in objs_status_dict:
      revisions.append(all_models.Revision.query.filter(
          all_models.Revision.resource_id == o_id,
          all_models.Revision.resource_type == o_type
      ))
    revisions_query = revisions[0].union(
        *revisions[1:]
    ).order_by(
        all_models.Revision.id
    )
    revisions_dict = collections.defaultdict(list)
    for revision in revisions_query:
      key = (revision.resource_type, revision.resource_id)
      revisions_dict[key].append(revision.content)
    for key, status in objs_status_dict.iteritems():
      self.assertIn(key, revisions_dict)
      content = revisions_dict[key][-1]
      self.assertIn("status", content)
      self.assertEqual(status, content["status"])

  def assert_searchable_by_status(self, *obj_status_chain):
    """Assert expected status in full text search."""
    objs_status_dict = {(o.type, o.id): s for o, s in obj_status_chain}
    full_text_properties = []
    for o_type, o_id in objs_status_dict:
      full_text_properties.append(
          mysql.MysqlRecordProperty.query.filter(
              mysql.MysqlRecordProperty.key == o_id,
              mysql.MysqlRecordProperty.type == o_type,
              mysql.MysqlRecordProperty.property == "task status",
          )
      )
    query = full_text_properties[0].union(*full_text_properties[1:])
    full_text_dict = {(f.type, f.key): f.content for f in query}
    for key, status in objs_status_dict.iteritems():
      self.assertIn(key, full_text_dict)
      self.assertEqual(status, full_text_dict[key])

  def assert_status_over_bulk_update(self, statuses, assert_statuses):
    """Assertion cycle_task statuses over bulk update."""
    self._update_ct_via_patch(statuses)
    self.refresh_set_up_instances()
    self.assertItemsEqual(assert_statuses, [obj.status for obj in self.tasks])
    obj_status_chain = [
        (t, assert_statuses[idx]) for idx, t in enumerate(self.tasks)
    ]
    self.assert_latest_revision_status(*obj_status_chain)
    self.assert_searchable_by_status(*obj_status_chain)

  def test_propagation_status_full(self):
    """Task status propagation for required verification workflow."""
    # all tasks in assigned state
    self.assertEqual([self.ASSIGNED] * 3, [t.status for t in self.tasks])
    # all tasks in progress state
    self.assert_status_over_bulk_update([self.IN_PROGRESS] * 3,
                                        [self.IN_PROGRESS] * 3)
    self.assertEqual(self.IN_PROGRESS, self.group.status)
    self.assertEqual(self.IN_PROGRESS, self.cycle.status)
    self.assertEqual(all_models.Workflow.ACTIVE, self.workflow.status)
    # update 1 task to finished
    self.assert_status_over_bulk_update(
        [self.FINISHED],
        [self.FINISHED, self.IN_PROGRESS, self.IN_PROGRESS])
    self.assertEqual(self.IN_PROGRESS, self.group.status)
    self.assertEqual(self.IN_PROGRESS, self.cycle.status)
    self.assertEqual(all_models.Workflow.ACTIVE, self.workflow.status)
    # all tasks moved to finished
    self.assert_status_over_bulk_update([self.FINISHED] * 3,
                                        [self.FINISHED] * 3)
    self.assertEqual(self.FINISHED, self.group.status)
    self.assertEqual(self.FINISHED, self.cycle.status)
    self.assertEqual(all_models.Workflow.ACTIVE, self.workflow.status)
    for task in self.tasks:
      self.assert_notifications_for_object(task,
                                           u'cycle_task_due_in',
                                           u'cycle_task_due_today',
                                           u'cycle_task_overdue')
    self.cycle = self.tasks[0].cycle
    self.assert_notifications_for_object(self.cycle)
    # all tasks moved to verified
    self.assert_status_over_bulk_update([self.VERIFIED] * 3,
                                        [self.VERIFIED] * 3)
    self.assertEqual(self.VERIFIED, self.group.status)
    self.assertEqual(self.VERIFIED, self.cycle.status)
    self.assertEqual(all_models.Workflow.INACTIVE, self.workflow.status)
    for task in self.tasks:
      self.assert_notifications_for_object(task)
    self.cycle = self.tasks[0].cycle
    self.assert_notifications_for_object(self.cycle,
                                         "all_cycle_tasks_completed")

  def test_propagation_status_short(self):
    """Task status propagation for not required verification workflow."""
    all_models.Cycle.query.filter(
        all_models.Cycle.id == self.cycle.id
    ).update({
        all_models.Cycle.is_verification_needed: False
    })
    db.session.commit()
    self.tasks = all_models.CycleTaskGroupObjectTask.query.order_by(
        all_models.CycleTaskGroupObjectTask.id
    ).all()
    # all tasks in assigned state
    self.assertEqual([self.ASSIGNED] * 3, [t.status for t in self.tasks])
    # all tasks in progress state
    self.assert_status_over_bulk_update([self.IN_PROGRESS] * 3,
                                        [self.IN_PROGRESS] * 3)
    self.assertEqual(self.IN_PROGRESS, self.group.status)
    self.assertEqual(self.IN_PROGRESS, self.cycle.status)
    self.assertEqual(all_models.Workflow.ACTIVE, self.workflow.status)
    # update 1 task to finished
    self.assert_status_over_bulk_update(
        [self.FINISHED],
        [self.FINISHED, self.IN_PROGRESS, self.IN_PROGRESS])
    self.assertEqual(self.IN_PROGRESS, self.group.status)
    self.assertEqual(self.IN_PROGRESS, self.cycle.status)
    self.assertEqual(all_models.Workflow.ACTIVE, self.workflow.status)
    self.assert_notifications_for_object(self.tasks[0])
    for task in self.tasks[1:]:
      self.assert_notifications_for_object(task,
                                           u'cycle_task_due_in',
                                           u'cycle_task_due_today',
                                           u'cycle_task_overdue')
    self.cycle = self.tasks[0].cycle
    self.assert_notifications_for_object(self.cycle)
    # all tasks moved to finished
    self.assert_status_over_bulk_update([self.FINISHED] * 3,
                                        [self.FINISHED] * 3)
    self.assertEqual(self.FINISHED, self.group.status)
    self.assertEqual(self.FINISHED, self.cycle.status)
    self.assertEqual(all_models.Workflow.INACTIVE, self.workflow.status)
    for task in self.tasks:
      self.assert_notifications_for_object(task)
    self.cycle = self.tasks[0].cycle
    self.assert_notifications_for_object(self.cycle,
                                         "all_cycle_tasks_completed")

  def test_deprecated_final(self):
    """Test task status propagation for deprecated workflow."""
    self.assertEqual([self.ASSIGNED] * 3, [t.status for t in self.tasks])
    # all tasks in progress state
    self.assert_status_over_bulk_update([self.DEPRECATED] * 3,
                                        [self.DEPRECATED] * 3)
    self.assertEqual(self.DEPRECATED, self.group.status)
    self.assertEqual(self.DEPRECATED, self.cycle.status)
    self.assertEqual(all_models.Workflow.ACTIVE, self.workflow.status)
    self.assert_status_over_bulk_update(
        [self.ASSIGNED, self.VERIFIED, self.FINISHED],
        [self.DEPRECATED] * 3)
    self.assertEqual(self.DEPRECATED, self.group.status)
    self.assertEqual(self.DEPRECATED, self.cycle.status)
    self.assertEqual(all_models.Workflow.ACTIVE, self.workflow.status)

  def test_update_tasks_from_2_cycles(self):
    """Test bulk update few cycles at the same time."""
    with factories.single_commit():
      _, _, group, _ = self._create_cycle_structure()
    group_id = group.id
    all_models.Cycle.query.update({
        all_models.Cycle.is_verification_needed: False
    })
    db.session.commit()
    self.tasks = all_models.CycleTaskGroupObjectTask.query.order_by(
        all_models.CycleTaskGroupObjectTask.id
    ).all()
    # all tasks in assigned state
    self.assertEqual([self.ASSIGNED] * 6, [t.status for t in self.tasks])
    # all tasks in progress state
    self.assert_status_over_bulk_update([self.IN_PROGRESS] * 6,
                                        [self.IN_PROGRESS] * 6)
    group = all_models.CycleTaskGroup.query.get(group_id)
    self.assertEqual(self.IN_PROGRESS, self.group.status)
    self.assertEqual(self.IN_PROGRESS, group.status)
    self.assertEqual(self.IN_PROGRESS, self.cycle.status)
    self.assertEqual(self.IN_PROGRESS, group.cycle.status)
    self.assertEqual(all_models.Workflow.ACTIVE, self.workflow.status)
    self.assertEqual(all_models.Workflow.ACTIVE, group.cycle.workflow.status)
    # update 1 task to finished
    self.assert_status_over_bulk_update(
        [self.FINISHED],
        [self.FINISHED] + [self.IN_PROGRESS] * 5)
    group = all_models.CycleTaskGroup.query.get(group_id)
    self.assertEqual(self.IN_PROGRESS, self.group.status)
    self.assertEqual(self.IN_PROGRESS, group.status)
    self.assertEqual(self.IN_PROGRESS, self.cycle.status)
    self.assertEqual(self.IN_PROGRESS, group.cycle.status)
    self.assertEqual(all_models.Workflow.ACTIVE, self.workflow.status)
    self.assertEqual(all_models.Workflow.ACTIVE, group.cycle.workflow.status)
    self.assert_notifications_for_object(self.tasks[0])
    for task in self.tasks[1:]:
      self.assert_notifications_for_object(task,
                                           u'cycle_task_due_in',
                                           u'cycle_task_due_today',
                                           u'cycle_task_overdue')
    self.assert_notifications_for_object(self.group.cycle)
    self.assert_notifications_for_object(group.cycle)
    # all tasks moved to finished
    self.assert_status_over_bulk_update([self.FINISHED] * 6,
                                        [self.FINISHED] * 6)
    group = all_models.CycleTaskGroup.query.get(group_id)
    self.assertEqual(self.FINISHED, self.group.status)
    self.assertEqual(self.FINISHED, group.status)
    self.assertEqual(self.FINISHED, self.cycle.status)
    self.assertEqual(self.FINISHED, group.cycle.status)
    self.assertEqual(all_models.Workflow.INACTIVE, self.workflow.status)
    self.assertEqual(all_models.Workflow.INACTIVE, group.cycle.workflow.status)
    for task in self.tasks:
      self.assert_notifications_for_object(task)
    self.assert_notifications_for_object(self.cycle,
                                         "all_cycle_tasks_completed")
    self.assert_notifications_for_object(group.cycle,
                                         "all_cycle_tasks_completed")
