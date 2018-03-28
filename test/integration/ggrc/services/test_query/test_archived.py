# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Tests for /query api endpoint."""

import ddt

from ggrc.models import all_models

from integration.ggrc import TestCase
from integration.ggrc.api_helper import Api
from integration.ggrc.models import factories
from integration.ggrc.query_helper import WithQueryApi


@ddt.ddt
class TestArchived(WithQueryApi, TestCase):
    """Tests for filtering by Archived field."""

    def setUp(self):
        super(TestArchived, self).setUp()
        self.client.get("/login")
        self.api = Api()

    @ddt.data([1, 3])
    def test_archived_audits(self, archived_audits):
        """Test filtration by Archived Audits."""
        with factories.single_commit():
            audit_ids = [factories.AuditFactory().id for _ in range(5)]

        expected_ids = []
        for i in archived_audits:
            audit = all_models.Audit.query.get(audit_ids[i])
            response = self.api.put(audit, {"archived": True})
            self.assert200(response)
            expected_ids.append(audit_ids[i])

        ids = self.simple_query(
            "Audit",
            expression=["archived", "=", "true"],
            type_="ids",
            field="ids")
        self.assertItemsEqual(ids, expected_ids)

    @ddt.data([2, 4])
    def test_archived_assessments(self, archived_audits):
        """Test filtration by Archived Assessments."""
        # Create 5 Audits, each of them has 3 Assessment
        with factories.single_commit():
            audit_ids = []
            for _ in range(5):
                audit = factories.AuditFactory()
                audit_ids.append(audit.id)
                for _ in range(3):
                    factories.AssessmentFactory(audit=audit)

        # This list contain ids of assessments from audits in archived_audits
        expected_ids = []
        for i in archived_audits:
            audit = all_models.Audit.query.get(audit_ids[i])
            expected_ids += [a.id for a in audit.assessments]
            response = self.api.put(audit, {"archived": True})
            self.assert200(response)

        ids = self.simple_query(
            "Assessment",
            expression=["archived", "=", "true"],
            type_="ids",
            field="ids")
        self.assertItemsEqual(ids, expected_ids)
