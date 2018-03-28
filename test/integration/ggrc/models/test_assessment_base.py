# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Test assessment base class used by test_assessment and
   test_assessment_generation modules"""

from ggrc.access_control.role import get_custom_roles_for
from ggrc.models import all_models

from integration import ggrc


class TestAssessmentBase(ggrc.TestCase):
    """Base class for Assessment tests"""

    def setUp(self):
        super(TestAssessmentBase, self).setUp()
        self.api = ggrc.api_helper.Api()
        self.assignee_roles = {
            role_name: role_id
            for role_id, role_name in get_custom_roles_for("Assessment")
            .items() if role_name in ["Assignees", "Creators", "Verifiers"]
        }

    def assert_mapped_role(self, role, person_email, mapped_obj):
        """Check if required role was created for mapped object"""
        query = all_models.AccessControlList.query.join(
            all_models.AccessControlRole, all_models.AccessControlRole.id ==
            all_models.AccessControlList.ac_role_id).join(
                all_models.Person,
                all_models.Person.id == all_models.AccessControlList.person_id
            ).filter(
                all_models.AccessControlList.object_id == mapped_obj.id,
                all_models.AccessControlList.object_type == mapped_obj.type,
                all_models.Person.email == person_email,
                all_models.AccessControlRole.name == role,
            )
        self.assertEqual(query.count(), 1)

    def assessment_post(self, template=None, extra_data=None):
        """Helper function to POST an assessment"""
        assessment_dict = {
            "_generated": True,
            "audit": {
                "id": self.audit.id,
                "type": "Audit"
            },
            "object": {
                "id": self.snapshot.id,
                "type": "Snapshot"
            },
            "context": {
                "id": self.audit.context.id,
                "type": "Context"
            },
            "title": "Temp title"
        }
        if template:
            assessment_dict["template"] = {
                "id": template.id,
                "type": "AssessmentTemplate"
            }
        if extra_data:
            assessment_dict.update(extra_data)

        response = self.api.post(all_models.Assessment,
                                 {"assessment": assessment_dict})
        if response.status_code == 201:
            id_ = response.json['assessment']['id']
            return self.api.get(all_models.Assessment, id_)
        return response
