# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Test for acl proposal api."""

import collections

from ggrc.models import all_models

from integration.ggrc.models import factories
from integration.ggrc.proposal.api import base


class TestACLProposalsApi(base.BaseTestProposalApi):
  """Test case for proposal acl api."""

  def test_proposal_for_acl(self):
    """Test simple add acl proposal."""
    with factories.single_commit():
      control = factories.ControlFactory(title="1")
      role = factories.AccessControlRoleFactory(name="role")
      person = factories.PersonFactory()
    control_id = control.id
    role_id = unicode(role.id)
    person_id = person.id
    control_content = control.log_json()
    control_content["access_control_list"] = [
        {"ac_role_id": role_id, "person": {"type": "Person", "id": person.id}}
    ]
    self.assertTrue(
        all_models.AccessControlRole.query.get(
            role_id
        ).is_delete_allowed)
    self.create_proposal(control,
                         full_instance_content=control_content,
                         agenda="update access control roles",
                         context=None)
    self.assertFalse(
        all_models.AccessControlRole.query.get(
            role_id
        ).is_delete_allowed)
    control = all_models.Control.query.get(control_id)
    self.assertEqual(1, len(control.proposals))
    self.assertIn("access_control_list", control.proposals[0].content)
    acl = control.proposals[0].content["access_control_list"]
    self.assertIn(role_id, acl)
    role = control.proposals[0].content["access_control_list"][role_id]
    person = all_models.Person.query.get(person_id)
    self.assertEqual(
        {
            "added": [{"id": person_id, "email": person.email}],
            "deleted": [],
        },
        role)
    self.assertEqual(1, len(control.comments))

  def test_proposal_delete_acl(self):
    """Test simple delete acl proposal."""
    with factories.single_commit():
      control = factories.ControlFactory(title="1")
      role = factories.AccessControlRoleFactory(name="role")
      person = factories.PersonFactory()
      factories.AccessControlListFactory(
          person=person,
          ac_role=role,
          object=control,
      )
    with factories.single_commit():
      latest_revision = all_models.Revision.query.filter(
          all_models.Revision.resource_id == control.id,
          all_models.Revision.resource_type == control.type
      ).order_by(
          all_models.Revision.created_at.desc()
      ).first()
      latest_revision.content = control.log_json()

    control_id = control.id
    role_id = unicode(role.id)
    person_id = person.id
    control_content = control.log_json()
    control_content["access_control_list"] = []
    self.create_proposal(control,
                         full_instance_content=control_content,
                         agenda="delete access control roles",
                         context=None)
    control = all_models.Control.query.get(control_id)
    self.assertEqual(1, len(control.proposals))
    self.assertIn("access_control_list", control.proposals[0].content)
    acl = control.proposals[0].content["access_control_list"]
    self.assertIn(role_id, acl)
    role = control.proposals[0].content["access_control_list"][role_id]
    person = all_models.Person.query.get(person_id)
    self.assertEqual(
        {
            "added": [],
            "deleted": [{"id": person_id, "email": person.email}],
        },
        role)
    self.assertEqual(1, len(control.comments))

  def test_apply_acl(self):  # pylint: disable=too-many-locals
    """Test simple apply acl proposal."""
    with factories.single_commit():
      control = factories.ControlFactory(title="1")
      role_1 = factories.AccessControlRoleFactory(
          name="role_1", object_type="Control")
      role_2 = factories.AccessControlRoleFactory(
          name="role_2", object_type="Control")
      role_3 = factories.AccessControlRoleFactory(
          name="role_3", object_type="Control")
      role_4 = factories.AccessControlRoleFactory(
          name="role_4", object_type="Control")
      role_5 = factories.AccessControlRoleFactory(
          name="role_5", object_type="Control")
      person_1 = factories.PersonFactory()
      person_2 = factories.PersonFactory()
      person_3 = factories.PersonFactory()
      factories.AccessControlListFactory(
          person=person_1,
          ac_role=role_1,
          object=control,
      )
      factories.AccessControlListFactory(
          person=person_2,
          ac_role=role_2,
          object=control,
      )
      factories.AccessControlListFactory(
          person=person_3,
          ac_role=role_3,
          object=control,
      )
      for person in [person_1, person_2, person_3]:
        factories.AccessControlListFactory(
            person=person,
            ac_role=role_4,
            object=control,
        )

    with factories.single_commit():
      proposal = factories.ProposalFactory(
          instance=control,
          content={
              "access_control_list": {
                  role_1.id: {
                      "added": [{"id": person_2.id, "email": person_2.email}],
                      "deleted": []
                  },
                  role_2.id: {
                      "added": [{"id": person_1.id, "email": person_1.email}],
                      "deleted": [{"id": person_2.id, "email": person_2.email}]
                  },
                  role_3.id: {
                      "added": [{"id": person_3.id, "email": person_3.email}],
                      "deleted": [{"id": person_2.id, "email": person_2.email}]
                  },
                  role_4.id: {
                      "added": [],
                      "deleted": [{"id": person_1.id, "email": person_1.email},
                                  {"id": person_2.id, "email": person_2.email},
                                  {"id": person_3.id, "email": person_3.email}]
                  },
                  role_5.id: {
                      "added": [{"id": person_1.id, "email": person_1.email},
                                {"id": person_2.id, "email": person_2.email},
                                {"id": person_3.id, "email": person_3.email}],
                      "deleted": [],
                  },
              }
          },
          agenda="agenda content")
    control_id = control.id
    person_1_id = person_1.id
    person_2_id = person_2.id
    person_3_id = person_3.id
    role_1_id = role_1.id
    role_2_id = role_2.id
    role_3_id = role_3.id
    role_4_id = role_4.id
    role_5_id = role_5.id
    self.assertEqual(proposal.STATES.PROPOSED, proposal.status)
    with self.number_obj_revisions_for(control):
      self.apply_proposal(proposal)
    control = all_models.Control.query.get(control_id)
    result_dict = collections.defaultdict(set)
    for acl in control.access_control_list:
      result_dict[acl.ac_role_id].add(acl.person_id)
    self.assertEqual({person_1_id, person_2_id}, result_dict[role_1_id])
    self.assertEqual({person_1_id}, result_dict[role_2_id])
    self.assertEqual({person_3_id}, result_dict[role_3_id])
    self.assertEqual(set([]), result_dict[role_4_id])
    self.assertEqual({person_1_id, person_2_id, person_3_id},
                     result_dict[role_5_id])
