# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Test Assessment hooks"""

from ggrc.models import all_models
from ggrc.models.hooks import assessment
from integration.ggrc.models import factories
from integration.ggrc import TestCase


class TestAssessmentHook(TestCase):
    """TestAuditRoleProgation"""

    def setUp(self):
        super(TestAssessmentHook, self).setUp()
        control = factories.ControlFactory()
        with factories.single_commit():
            self.assessment = factories.AssessmentFactory()
            audit = factories.AuditFactory()
            revision = all_models.Revision.query.filter(
                all_models.Revision.resource_id == control.id,
                all_models.Revision.resource_type == control.type,
            ).first()
            self.snapshot = factories.SnapshotFactory(
                parent=audit,
                revision_id=revision.id,
                child_type=control.type,
                child_id=control.id,
            )

    def test_missing_snapshot_plan(self):
        """Test copy_snapshot_plan when test_plan is missing from revision"""
        self.snapshot.revision.content = {}
        assessment_test_plan = self.assessment.test_plan
        assessment.copy_snapshot_plan(self.assessment, self.snapshot)
        self.assertEqual(assessment_test_plan, self.assessment.test_plan)
