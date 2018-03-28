# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Integration tests for Program."""

from ggrc.models import all_models

from integration.ggrc import api_helper
from integration.ggrc.models import factories
from integration.ggrc import TestCase


class TestProgram(TestCase):
    """Program test cases."""

    def setUp(self):
        self.api = api_helper.Api()

        with factories.single_commit():
            self.program = factories.ProgramFactory()
            self.audit_id = factories.AuditFactory(program=self.program).id

    def test_put_empty_audits(self):
        """Audit doesn't get deleted when empty audits field is put."""
        response = self.api.put(self.program, data={"audits": []})

        self.assert200(response)
        audit = self.refresh_object(all_models.Audit, id_=self.audit_id)
        self.assertIsNotNone(audit)
