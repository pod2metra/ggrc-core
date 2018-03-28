# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""CycleTaskGroup model related tests."""

from ggrc.models import all_models
from integration.ggrc.models import factories
from integration.ggrc_workflows.helpers import rbac_helper
from integration.ggrc_workflows.helpers import workflow_test_case
from integration.ggrc_workflows.models import factories as wf_factories


class TestCycleTaskGroupApiCalls(workflow_test_case.WorkflowTestCase):
    """Tests related to CycleTaskGroup REST API calls."""

    def test_get_ctg_g_reader_no_role(self):
        """GET CycleTaskGroup collection logged in as GlobalReader & No Role."""
        with factories.single_commit():
            wf_factories.CycleTaskGroupFactory()
            self.setup_helper.setup_person(rbac_helper.GR_RNAME, "No Role")

        g_reader = self.setup_helper.get_person(rbac_helper.GR_RNAME,
                                                "No Role")
        self.api_helper.set_user(g_reader)

        cycle_task_group = all_models.CycleTaskGroup.query.one()
        response = self.api_helper.get_collection(cycle_task_group,
                                                  (cycle_task_group.id, ))
        self.assertTrue(
            response.json["cycle_task_groups_collection"]["cycle_task_groups"])
