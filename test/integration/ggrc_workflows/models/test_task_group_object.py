# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""TaskGroupObject model related tests."""

import ddt
import datetime
import time
from multiprocessing import Process, Queue

from ggrc.models import all_models
from ggrc_workflows import ac_roles
from integration.ggrc.models import factories
from integration.ggrc_workflows.helpers import workflow_api
from integration.ggrc_workflows.helpers import rbac_helper
from integration.ggrc_workflows.helpers import workflow_test_case
from integration.ggrc_workflows.models import factories as wf_factories


@ddt.ddt
class TestTaskGroupObjectApiCalls(workflow_test_case.WorkflowTestCase):
  """Tests related to TaskGroupObject REST API calls."""

  @ddt.data(
      rbac_helper.GA_RNAME,
      rbac_helper.GE_RNAME,
      rbac_helper.GR_RNAME,
      rbac_helper.GC_RNAME,
  )
  def test_map_obj_to_tg_g_role_admin(self, g_rname):
    """Map Control to TaskGroup logged in as {} & Admin."""
    with factories.single_commit():
      workflow = self.setup_helper.setup_workflow((g_rname,))
      wf_factories.TaskGroupFactory(workflow=workflow)
      factories.ControlFactory(directive=None)

    g_person = self.setup_helper.get_person(g_rname,
                                            ac_roles.workflow.ADMIN_NAME)
    self.api_helper.set_user(g_person)

    task_group = all_models.TaskGroup.query.one()
    control = all_models.Control.query.one()

    data = workflow_api.get_task_group_object_post_dict(task_group, control)
    response = self.api_helper.post(all_models.TaskGroupObject, data)
    self.assertEqual(response.status_code, 201)

  @ddt.data(
      rbac_helper.GA_RNAME,
      rbac_helper.GE_RNAME,
      rbac_helper.GR_RNAME,
      rbac_helper.GC_RNAME,
  )
  def test_unmap_obj_tg_g_role_admin(self, g_rname):
    """Unmap object from TaskGroup logged in as {} & Admin."""
    with factories.single_commit():
      workflow = self.setup_helper.setup_workflow((g_rname,))
      task_group = wf_factories.TaskGroupFactory(workflow=workflow)
      wf_factories.TaskGroupObjectFactory(task_group=task_group)

    g_person = self.setup_helper.get_person(g_rname,
                                            ac_roles.workflow.ADMIN_NAME)
    self.api_helper.set_user(g_person)

    task_group_object = all_models.TaskGroupObject.query.one()

    response = self.api_helper.delete(task_group_object)
    self.assertEqual(response.status_code, 200)

  def test_get_tgo_g_reader_no_role(self):
    """GET TaskGroupObject collection logged in as GlobalReader & No Role."""
    with factories.single_commit():
      wf_factories.TaskGroupObjectFactory()
      self.setup_helper.setup_person(rbac_helper.GR_RNAME, "No Role")

    g_reader = self.setup_helper.get_person(rbac_helper.GR_RNAME, "No Role")
    self.api_helper.set_user(g_reader)

    task_group_object = all_models.TaskGroupObject.query.one()
    response = self.api_helper.get_collection(task_group_object,
                                              (task_group_object.id, ))
    self.assertTrue(
        response.json["task_group_objects_collection"]["task_group_objects"]
    )

  def test_submit_for_review(self):
    with factories.single_commit():
      control = factories.ControlFactory()
      task_group = wf_factories.TaskGroupFactory()
      user = factories.PersonFactory()
      for idx in range(4):
        factories.AccessControlRoleFactory(object_type=control.type,
                                           name="test_{}".format(idx))
    tgt_name = all_models.TaskGroupTask.__name__
    acr = all_models.AccessControlRole.query.filter(
       all_models.AccessControlRole.name=="Task Assignees",
       all_models.AccessControlRole.object_type==tgt_name,
    ).one()

    tgt_data = workflow_api.get_task_post_dict(
        task_group,
        {"Task Assignees": user},
        datetime.date.today(),
        datetime.date.today(),
    )
    tgo_data = workflow_api.get_task_group_object_post_dict(task_group, control)

    def put_in_subprocess(queue, model, data):
      queue.put(self.api_helper.post(model, data).status_code)

    queue = Queue()
    th_create_obj = Process(target=put_in_subprocess,
                            args=(queue, all_models.TaskGroupObject, tgo_data))
    th_create_task = Process(target=put_in_subprocess,
                             args=(queue, all_models.TaskGroupTask, tgt_data))
    th_create_obj.start()
    th_create_task.start()
    th_create_obj.join(10)
    th_create_task.join(10)
    self.assertEqual(201, queue.get())
    self.assertEqual(201, queue.get())
