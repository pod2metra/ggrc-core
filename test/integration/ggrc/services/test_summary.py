# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Test /summary endpoint
"""
import ddt

from ggrc.models import all_models
from integration.ggrc import TestCase
from integration.ggrc.api_helper import Api
from integration.ggrc.models import factories


@ddt.ddt
class TestAuditSummary(TestCase):
    """Test /summary for Audit"""

    def setUp(self):
        """Set up for test methods."""
        super(TestAuditSummary, self).setUp()
        self.api = Api()

    @ddt.data(1, 2)
    def test_audit_summary(self, assessment_count):
        """Test Audit summary when each type of Asmnt linked to each Doc type"""
        with factories.single_commit():
            audit = factories.AuditFactory()
            for status in all_models.Assessment.VALID_STATES:
                for _ in range(assessment_count):
                    asmnt = factories.AssessmentFactory(
                        audit=audit, status=status)
                    for doc_type in all_models.Document.VALID_DOCUMENT_TYPES:
                        doc = factories.DocumentFactory(document_type=doc_type)
                        factories.RelationshipFactory(
                            source=asmnt, destination=doc)

        summary_link = "/api/{}/{}/summary".format(
            audit._inflector.table_plural, audit.id)
        response = self.api.client.get(summary_link)
        self.assert200(response)

        doc_count = len(all_models.Document.VALID_DOCUMENT_TYPES)
        expected_data = {
            "statuses": [{
                "name": "Completed",
                "assessments": assessment_count,
                "documents": doc_count * assessment_count,
                "verified": 0
            }, {
                "name": "Completed",
                "assessments": assessment_count,
                "documents": doc_count * assessment_count,
                "verified": 1
            }, {
                "name": "Deprecated",
                "assessments": assessment_count,
                "documents": doc_count * assessment_count,
                "verified": 0
            }, {
                "name": "In Progress",
                "assessments": assessment_count,
                "documents": doc_count * assessment_count,
                "verified": 0
            }, {
                "name": "In Review",
                "assessments": assessment_count,
                "documents": doc_count * assessment_count,
                "verified": 0
            }, {
                "name": "Not Started",
                "assessments": assessment_count,
                "documents": doc_count * assessment_count,
                "verified": 0
            }, {
                "name": "Rework Needed",
                "assessments": assessment_count,
                "documents": doc_count * assessment_count,
                "verified": 0
            }],
            "total": {
                "assessments": 7 * assessment_count,
                "documents": 7 * doc_count * assessment_count
            }
        }
        self.assertEqual(response.json, expected_data)

    def test_asmnt_map_same_docs(self):
        """Test Audit summary when all Assessments mapped to same Documents"""
        with factories.single_commit():
            audit = factories.AuditFactory()
            asmnt_statuses = all_models.Assessment.VALID_STATES
            docs = [
                factories.DocumentFactory(document_type=doc_type)
                for doc_type in all_models.Document.VALID_DOCUMENT_TYPES
            ]
            for status in asmnt_statuses:
                asmnt = factories.AssessmentFactory(audit=audit, status=status)
                for doc in docs:
                    factories.RelationshipFactory(
                        source=asmnt, destination=doc)

        summary_link = "/api/{}/{}/summary".format(
            audit._inflector.table_plural, audit.id)
        response = self.api.client.get(summary_link)
        self.assert200(response)

        doc_count = len(all_models.Document.VALID_DOCUMENT_TYPES)
        expected_data = {
            "statuses": [{
                "name": "Completed",
                "assessments": 1,
                "documents": doc_count,
                "verified": 0
            }, {
                "name": "Completed",
                "assessments": 1,
                "documents": doc_count,
                "verified": 1
            }, {
                "name": "Deprecated",
                "assessments": 1,
                "documents": doc_count,
                "verified": 0
            }, {
                "name": "In Progress",
                "assessments": 1,
                "documents": doc_count,
                "verified": 0
            }, {
                "name": "In Review",
                "assessments": 1,
                "documents": doc_count,
                "verified": 0
            }, {
                "name": "Not Started",
                "assessments": 1,
                "documents": doc_count,
                "verified": 0
            }, {
                "name": "Rework Needed",
                "assessments": 1,
                "documents": doc_count,
                "verified": 0
            }],
            "total": {
                "assessments": 7,
                "documents": doc_count
            }
        }
        self.assertEqual(response.json, expected_data)

    def test_part_asmnt_exist(self):
        """Test Audit summary when not all kinds of Asmnt created"""
        with factories.single_commit():
            audit = factories.AuditFactory()
            for status in ["Completed", "Verified"]:
                asmnt = factories.AssessmentFactory(audit=audit, status=status)
                for doc_type in all_models.Document.VALID_DOCUMENT_TYPES:
                    doc = factories.DocumentFactory(document_type=doc_type)
                    factories.RelationshipFactory(
                        source=asmnt, destination=doc)

        summary_link = "/api/{}/{}/summary".format(
            audit._inflector.table_plural, audit.id)
        response = self.api.client.get(summary_link)
        self.assert200(response)

        doc_count = len(all_models.Document.VALID_DOCUMENT_TYPES)
        expected_data = {
            "statuses": [
                {
                    "name": "Completed",
                    "assessments": 1,
                    "documents": doc_count,
                    "verified": 0
                },
                {
                    "name": "Completed",
                    "assessments": 1,
                    "documents": doc_count,
                    "verified": 1
                },
            ],
            "total": {
                "assessments": 2,
                "documents": 2 * doc_count
            }
        }
        self.assertEqual(response.json, expected_data)

    def test_empty_audit_summary(self):
        """Test Audit summary if there are no assessments"""
        audit = factories.AuditFactory()

        summary_link = "/api/{}/{}/summary".format(
            audit._inflector.table_plural, audit.id)
        response = self.api.client.get(summary_link)
        expected_data = {
            "statuses": [],
            "total": {
                "assessments": 0,
                "documents": 0,
            }
        }
        self.assertEqual(response.json, expected_data)
