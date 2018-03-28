# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""TaskGroupObject model related tests."""

import ddt

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
            workflow = self.setup_helper.setup_workflow((g_rname, ))
            wf_factories.TaskGroupFactory(workflow=workflow)
            factories.ControlFactory(directive=None)

        g_person = self.setup_helper.get_person(g_rname,
                                                ac_roles.workflow.ADMIN_NAME)
        self.api_helper.set_user(g_person)

        task_group = all_models.TaskGroup.query.one()
        control = all_models.Control.query.one()

        data = workflow_api.get_task_group_object_post_dict(
            task_group, control)
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
            workflow = self.setup_helper.setup_workflow((g_rname, ))
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

        g_reader = self.setup_helper.get_person(rbac_helper.GR_RNAME,
                                                "No Role")
        self.api_helper.set_user(g_reader)

        task_group_object = all_models.TaskGroupObject.query.one()
        response = self.api_helper.get_collection(task_group_object,
                                                  (task_group_object.id, ))
        self.assertTrue(response.json["task_group_objects_collection"][
            "task_group_objects"])
