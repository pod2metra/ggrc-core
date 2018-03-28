# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Test Access Control List"""

import ddt

from ggrc import db
from ggrc.access_control.role import get_custom_roles_for
from ggrc.models import all_models
from integration.ggrc import TestCase
from integration.ggrc.models import factories
from integration.ggrc.api_helper import Api
from integration.ggrc.generator import ObjectGenerator


class TestRBAC(TestCase):
    """TestRBAC base class with batch of helper methods"""

    def set_up_people(self):
        """Set up people with different roles needed by the tests"""
        self.people = {}
        object_generator = ObjectGenerator()

        for name in ["Creator", "Reader", "Editor"]:
            _, user = object_generator.generate_person(
                data={"name": name}, user_role=name)
            self.people[name] = user

    def set_up_acl_object(self):
        """Set up a control with an access control role that grants RUD"""
        self.control = factories.ControlFactory()
        self.all_acr = factories.AccessControlRoleFactory(
            object_type="Control", read=True, update=True, delete=True)
        for name in ["Creator", "Reader", "Editor"]:
            factories.AccessControlListFactory(
                object=self.control,
                ac_role_id=self.all_acr.id,
                person=self.people.get(name))


@ddt.ddt
class TestAccessControlRBAC(TestRBAC):
    """TestAccessControlRBAC tests if users get correct permissions on objects
     from the access control table"""

    def setUp(self):
        super(TestAccessControlRBAC, self).setUp()
        self.api = Api()
        self.set_up_people()
        self.set_up_acl_object()

    @ddt.data("Creator", "Reader", "Editor")
    def test_acl_object_cru(self, name):
        """Test if {0} can CRUD an object with all permissions"""
        control_id = self.control.id
        person = self.people.get(name)
        role_id = self.all_acr.id
        db.session.add(person)
        self.api.set_user(person)
        response = self.api.get(all_models.Control, control_id)
        assert response.status_code == 200, \
            "{} cannot GET object from acl. Received {}".format(
                name, response.status)
        acl = response.json["control"]["access_control_list"]
        assert len(response.json["control"]["access_control_list"]) == 3, \
            "ACL in control does not include all people {}".format(acl)

        assert acl[0].get("ac_role_id", None) == role_id, \
            "ACL list does not include role id {}".format(acl)


class TestAssigneeRBAC(TestRBAC):
    """TestAssigneeRBAC tests if users get correct permissions on objects
  where he is has assignee role"""

    def setUp(self):
        super(TestAssigneeRBAC, self).setUp()
        self.api = Api()
        self.set_up_people()
        self.assignee_roles = {
            role_name: role_id
            for role_id, role_name in get_custom_roles_for("Assessment")
            .items() if role_name in ["Assignees", "Creators", "Verifiers"]
        }

    def test_mapped_regulations_read(self):
        """Test if creators can CRUD mapped Regulations and Objective snapshots."""
        self.api.set_user(self.people.get("Editor"))
        with factories.single_commit():
            audit = factories.AuditFactory()
            assessment = factories.AssessmentFactory(audit=audit)
            factories.AccessControlListFactory(
                ac_role_id=self.assignee_roles["Creators"],
                person=self.people.get("Editor"),
                object=assessment)
            factories.AccessControlListFactory(
                ac_role_id=self.assignee_roles["Assignees"],
                person=self.people.get("Creator"),
                object=assessment)
            factories.RelationshipFactory(source=audit, destination=assessment)
            control = factories.ControlFactory()
            objective = factories.ObjectiveFactory()
            regulation = factories.RegulationFactory()
            snapshots = self._create_snapshots(
                audit, [control, objective, regulation])
            factories.RelationshipFactory(
                source=snapshots[0], destination=snapshots[1])
            factories.RelationshipFactory(
                source=snapshots[2], destination=snapshots[0])
            factories.RelationshipFactory(
                source=assessment, destination=snapshots[0])

        self.api.set_user(self.people.get("Creator"))
        for snapshot in snapshots:
            db.session.add(snapshot)
            response = self.api.get(type(snapshot), snapshot.id)
            self.assertEqual(response.status_code, 200,
                             "Cannot GET mapped object. Received {}".format(
                                 response.status))
            db.session.add(snapshot)
            response = self.api.delete(snapshot)
            self.assertEqual(response.status_code, 403,
                             "Can DELETE mapped object. Received {}".format(
                                 response.status))
