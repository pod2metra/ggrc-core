# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""CycleTaskEntry model related tests."""

from ggrc.models import all_models
from ggrc_workflows import ac_roles
from integration.ggrc.models import factories
from integration.ggrc_workflows.helpers import rbac_helper
from integration.ggrc_workflows.helpers import workflow_api
from integration.ggrc_workflows.helpers import workflow_test_case
from integration.ggrc_workflows.models import factories as wf_factories


class TestCommentApiCalls(workflow_test_case.WorkflowTestCase):
    """Tests related to CycleTaskEntry REST API calls."""

    def test_post_comment_editor_admin(self):
        """POST CycleTaskEntry logged in as GlobalEditor & WF Admin."""
        with factories.single_commit():
            workflow = self.setup_helper.setup_workflow(
                (rbac_helper.GE_RNAME, ))
            cycle = wf_factories.CycleFactory(workflow=workflow)
            wf_factories.CycleTaskFactory(cycle=cycle)

        g_editor = self.setup_helper.get_person(rbac_helper.GE_RNAME,
                                                ac_roles.workflow.ADMIN_NAME)
        self.api_helper.set_user(g_editor)

        cycle_task = all_models.CycleTaskGroupObjectTask.query.one()

        data = workflow_api.get_cycle_task_entry_post_dict(cycle_task)
        response = self.api_helper.post(all_models.CycleTaskEntry, data)
        self.assertEqual(response.status_code, 201)

    def test_get_cte_g_reader_no_role(self):
        """GET CycleTaskEntry collection logged in as GlobalReader & No Role."""
        with factories.single_commit():
            wf_factories.CycleTaskEntryFactory()
            self.setup_helper.setup_person(rbac_helper.GR_RNAME, "No Role")

        g_reader = self.setup_helper.get_person(rbac_helper.GR_RNAME,
                                                "No Role")
        self.api_helper.set_user(g_reader)

        comment = all_models.CycleTaskEntry.query.one()
        response = self.api_helper.get_collection(comment, (comment.id, ))
        self.assertTrue(response.json["cycle_task_entries_collection"][
            "cycle_task_entries"])
