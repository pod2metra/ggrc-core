# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Workflow test case base class definition."""

from integration.ggrc import TestCase
from integration.ggrc import api_helper
from integration.ggrc_workflows.helpers import setup_helper


class WorkflowTestCase(TestCase):
    """Workflow test case base class."""

    def setUp(self):
        super(WorkflowTestCase, self).setUp()
        self.api_helper = api_helper.Api()
        self.setup_helper = setup_helper.WorkflowSetup()
