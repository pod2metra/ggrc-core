# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""TaskGroupTask model related tests."""

import ddt

from ggrc.models import all_models
from ggrc_workflows import ac_roles
from integration.ggrc.models import factories
from integration.ggrc_workflows.helpers import rbac_helper
from integration.ggrc_workflows.helpers import workflow_api
from integration.ggrc_workflows.helpers import workflow_test_case
from integration.ggrc_workflows.models import factories as wf_factories


@ddt.ddt
class TestTaskApiCalls(workflow_test_case.WorkflowTestCase):
    """Tests related to TaskGroupTask REST API calls."""

    @ddt.data(
        rbac_helper.GA_RNAME,
        rbac_helper.GE_RNAME,
        rbac_helper.GR_RNAME,
        rbac_helper.GC_RNAME,
    )
    def test_post_task_g_role_admin(self, g_rname):
        """POST TaskGroupTask logged in as {} & WF Admin."""
        with factories.single_commit():
            workflow = self.setup_helper.setup_workflow((g_rname, ))
            wf_factories.TaskGroupFactory(workflow=workflow)

        g_person = self.setup_helper.get_person(g_rname,
                                                ac_roles.workflow.ADMIN_NAME)
        self.api_helper.set_user(g_person)

        task_group = all_models.TaskGroup.query.one()
        people_roles = {ac_roles.task.ASSIGNEE_NAME: g_person}

        data = workflow_api.get_task_post_dict(task_group, people_roles,
                                               "2018-01-01", "2018-01-02")
        response = self.api_helper.post(all_models.TaskGroupTask, data)
        self.assertEqual(response.status_code, 201)

    def test_get_task_g_reader_no_role(self):
        """GET TaskGroupTask collection logged in as GlobalReader & No Role."""
        with factories.single_commit():
            wf_factories.TaskGroupTaskFactory()
            self.setup_helper.setup_person(rbac_helper.GR_RNAME, "No Role")

        g_reader = self.setup_helper.get_person(rbac_helper.GR_RNAME,
                                                "No Role")
        self.api_helper.set_user(g_reader)

        task_group_task = all_models.TaskGroupTask.query.one()
        response = self.api_helper.get_collection(task_group_task,
                                                  (task_group_task.id, ))
        self.assertTrue(
            response.json["task_group_tasks_collection"]["task_group_tasks"])

    def test_post_task_g_editor_no_role(self):
        """POST TaskGroupTask logged in as GlobalEditor & No Role."""
        with factories.single_commit():
            wf_factories.TaskGroupFactory()
            self.setup_helper.setup_person(rbac_helper.GE_RNAME, "No Role")
            self.setup_helper.setup_person(rbac_helper.GA_RNAME, "No Role")

        g_editor = self.setup_helper.get_person(rbac_helper.GE_RNAME,
                                                "No Role")
        self.api_helper.set_user(g_editor)

        g_admin = self.setup_helper.get_person(rbac_helper.GA_RNAME, "No Role")
        people_roles = {ac_roles.task.ASSIGNEE_NAME: g_admin}
        task_group = all_models.TaskGroup.query.one()
        data = workflow_api.get_task_post_dict(task_group, people_roles,
                                               "2018-01-01", "2018-01-02")

        response = self.api_helper.post(all_models.TaskGroupTask, data)
        self.assertEqual(response.status_code, 201)
