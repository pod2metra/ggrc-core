# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Tests for AssessmentTemplate model."""
from ggrc.models import all_models

from integration.ggrc import TestCase, Api
from integration.ggrc.models import factories


class TestAssessmentTemplate(TestCase):
    """ Test AssessmentTemplate class. """

    def setUp(self):
        super(TestAssessmentTemplate, self).setUp()
        self.api = Api()

    def test_audit_setup(self):
        """Test audit setup for assessment_template"""
        audit = factories.AuditFactory()
        response = self.api.post(
            all_models.AssessmentTemplate, {
                "assessment_template": {
                    "audit": {
                        "id": audit.id
                    },
                    "context": {
                        "id": audit.context.id
                    },
                    "default_people": {
                        "assignees": "Admin",
                        "verifiers": "Admin",
                    },
                    "title": "Some title"
                }
            })
        self.assertStatus(response, 201)
        template_id = response.json["assessment_template"]["id"]
        template = all_models.AssessmentTemplate.query.get(template_id)
        self.assertEqual(template.audit.id, audit.id)

    def test_audit_issue_tracker(self):
        """Test existing audit issue_tracker info in template response"""
        with factories.single_commit():
            audit = factories.AuditFactory()
            audit_id = audit.id
            factories.IssueTrackerIssueFactory(
                issue_tracked_obj=audit,
                component_id="some id",
                hotlist_id="some host id",
            )
            template_id = factories.AssessmentTemplateFactory(
                audit=audit, context=audit.context).id
        response = self.api.get(all_models.AssessmentTemplate, template_id)
        self.assert200(response)
        audit = all_models.Audit.query.get(audit_id)
        self.assertEqual(
            response.json["assessment_template"]["audit"], {
                "type": "Audit",
                "id": audit.id,
                "href": "/api/audits/{}".format(audit.id),
                "context_id": audit.context.id,
                "issue_tracker": {
                    "component_id": "some id",
                    "enabled": False,
                    "issue_severity": None,
                    "hotlist_id": "some host id",
                    "issue_priority": None,
                    "issue_type": None
                }
            })
