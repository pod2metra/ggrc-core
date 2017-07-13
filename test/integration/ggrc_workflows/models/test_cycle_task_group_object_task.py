# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Module for integration tests for CycleTaskGroupObjectTask specifics."""

import datetime
import ddt

from ggrc import db
from ggrc.models import all_models

from integration.ggrc import TestCase as BaseTestCase
from integration.ggrc import api_helper
from integration.ggrc.models import factories
from integration.ggrc_basic_permissions.models import factories as bp_factories
from integration.ggrc_workflows import generator as wf_generator
from integration.ggrc_workflows.models import factories as wf_factories


@ddt.ddt
class TestCTGOT(BaseTestCase):
  """Test suite for CycleTaskGroupObjectTask specific logic."""

  NOBODY = "nobody@example.com"
  WORKFLOW_OWNER = "wfo@example.com"
  TASK_ASSIGNEE_1 = "assignee_1@example.com"
  TASK_ASSIGNEE_2 = "assignee_2@example.com"

  def setUp(self):
    super(TestCTGOT, self).setUp()

    self.api = api_helper.Api()

    with factories.single_commit():
      assignee_1 = factories.PersonFactory(email=self.TASK_ASSIGNEE_1)
      assignee_2 = factories.PersonFactory(email=self.TASK_ASSIGNEE_2)
      workflow_owner = factories.PersonFactory(email=self.WORKFLOW_OWNER)
      nobody = factories.PersonFactory(email=self.NOBODY)

      workflow_owner_role = (all_models.Role.query
                             .filter_by(name="WorkflowOwner").one())
      reader_role = all_models.Role.query.filter_by(name="Reader").one()
      for person in [assignee_1, assignee_2, workflow_owner, nobody]:
        bp_factories.UserRoleFactory(person=person,
                                     role=reader_role,
                                     context=None)

      workflow = wf_factories.WorkflowFactory()
      taskgroup = wf_factories.TaskGroupFactory(workflow=workflow)
      wf_factories.TaskGroupTaskFactory(task_group=taskgroup,
                                        contact=assignee_1)
      wf_factories.TaskGroupTaskFactory(task_group=taskgroup,
                                        contact=assignee_2)
      bp_factories.UserRoleFactory(person=workflow_owner,
                                   role=workflow_owner_role,
                                   context=workflow.context)

    self.generator = wf_generator.WorkflowsGenerator()
    self.cycle_id = self.generator.generate_cycle(workflow)[1].id
    self.generator.activate_workflow(workflow)

  @ddt.data((NOBODY, [False, False]),
            (WORKFLOW_OWNER, [True, True]),
            (TASK_ASSIGNEE_1, [True, False]),
            (TASK_ASSIGNEE_2, [False, True]))
  @ddt.unpack
  def test_change_state_by_user(self, user, expected_values):
    """Test cycle task allow_change_state value by user position."""
    all_models.Cycle.query.filter(
        all_models.Cycle.id == self.cycle_id
    ).update({
        all_models.Cycle.is_current: True,
    })
    db.session.commit()
    user = all_models.Person.query.filter_by(email=user).one()
    self.api.set_user(user)
    response = self.api.get_query(all_models.CycleTaskGroupObjectTask,
                                  "__sort=id")
    self.assert200(response)

    cycle_tasks = (response.json
                           .get("cycle_task_group_object_tasks_collection", {})
                           .get("cycle_task_group_object_tasks", []))
    # relies on same order of ids of TGT and CTGOT
    self.assertListEqual(
        [cycle_task["allow_change_state"] for cycle_task in cycle_tasks],
        expected_values,
    )

  @ddt.data(True, False)
  def test_change_state_by_is_current(self, cycle_is_current):
    """Test cycle task allow_change_state value by Cycle is_current value."""
    all_models.Cycle.query.filter(
        all_models.Cycle.id == self.cycle_id
    ).update({
        all_models.Cycle.is_current: cycle_is_current,
    })
    db.session.commit()
    user_mail = self.WORKFLOW_OWNER
    user = all_models.Person.query.filter_by(email=user_mail).one()
    self.api.set_user(user)
    response = self.api.get_query(all_models.CycleTaskGroupObjectTask,
                                  "__sort=id")
    self.assert200(response)

    cycle_tasks = (response.json
                           .get("cycle_task_group_object_tasks_collection", {})
                           .get("cycle_task_group_object_tasks", []))
    # relies on same order of ids of TGT and CTGOT
    states = [ct["allow_change_state"] for ct in cycle_tasks]
    if cycle_is_current:
      self.assertTrue(all(states))
    else:
      self.assertFalse(any(states))

  def test_context_after_task_delete(self):
    """Test UserRoles context keeping after cycle task deletion."""
    workflow_owner_role = all_models.Role.query.filter_by(
        name="WorkflowOwner"
    ).one()
    ctask = all_models.CycleTaskGroupObjectTask.query.first()
    ctask_context_id = ctask.context_id
    self.assertTrue(ctask_context_id)

    user = all_models.Person.query.filter_by(email=self.WORKFLOW_OWNER).one()
    self.api.set_user(user)

    response = self.api.delete(ctask)
    self.assert200(response)

    user_role = all_models.UserRole.query.filter_by(
        role_id=workflow_owner_role.id,
        person_id=user.id,
    ).one()
    self.assertEqual(user_role.context_id, ctask_context_id)

    for ctask in all_models.CycleTaskGroupObjectTask.query.all():
      self.assertEqual(ctask.context_id, ctask_context_id)

  @ddt.data("InProgress", "Finished", "Verified", "Declined")
  def test_log_state(self, state):
    all_models.Protocol.query.delete()
    cycle = all_models.Cycle.query.get(self.cycle_id)
    task = cycle.cycle_task_group_object_tasks[0]
    task_id = task.id
    task = all_models.CycleTaskGroupObjectTask.query.get(task_id)
    field_name = "{}_date".format(state.lower())
    self.assertIsNone(getattr(task, field_name))
    self.generator.modify_object(task, {"status": state})
    task = all_models.CycleTaskGroupObjectTask.query.get(task_id)
    self.assertLessEqual(datetime.datetime.now() - getattr(task, field_name),
                         datetime.timedelta(seconds=2))
    self.assertEqual(1, len(task._date_logs_map[state.lower()]))
