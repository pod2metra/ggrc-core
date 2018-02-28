# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Test for proposal cav api."""

import ddt

from ggrc.models import all_models

from integration.ggrc.models import factories
from integration.ggrc.proposal.api import base


@ddt.ddt
class TestCADProposalsApi(base.BaseTestProposalApi):
  """Test for proposal cav api."""

  @ddt.data(True, False)
  def test_change_cad(self, cav_empty):
    """Test create proposal with change CAVs."""
    with factories.single_commit():
      control = factories.ControlFactory(title="1")
      cad = factories.CustomAttributeDefinitionFactory(
          definition_type="control")
      if not cav_empty:
        factories.CustomAttributeValueFactory(
            custom_attribute=cad,
            attributable=control,
            attribute_value="123")
    control_id = control.id
    cad_id = cad.id
    data = control.log_json()
    del data["custom_attributes"]
    data["custom_attribute_values"] = [{
        "custom_attribute_id": cad_id,
        "attribute_value": "321",
        "attribute_object_id": None,
    }]
    self.assertEqual(
        cav_empty,
        all_models.CustomAttributeDefinition.query.get(
            cad_id
        ).is_delete_allowed)
    self.create_proposal(control,
                         full_instance_content=data,
                         agenda="update cav",
                         context=None)
    self.assertFalse(
        all_models.CustomAttributeDefinition.query.get(
            cad_id
        ).is_delete_allowed)
    control = all_models.Control.query.get(control_id)
    self.assertEqual(1, len(control.proposals))
    self.assertIn("custom_attribute_values", control.proposals[0].content)
    self.assertEqual({unicode(cad_id): {"attribute_value": u"321",
                                        "attribute_object": None}},
                     control.proposals[0].content["custom_attribute_values"])
    self.assertEqual(1, len(control.comments))

  def test_apply_cad(self):
    """Test apply proposal with change CAVs."""
    with factories.single_commit():
      control = factories.ControlFactory(title="1")
      cad = factories.CustomAttributeDefinitionFactory(
          definition_type="control")
    control_id = control.id
    proposal = factories.ProposalFactory(
        instance=control,
        content={
            "custom_attribute_values": {
                cad.id: {
                    "attribute_value": "321",
                    "attribute_object": None,
                },
            },
        },
        agenda="agenda content")
    with self.number_obj_revisions_for(control):
      self.apply_proposal(proposal)
    control = all_models.Control.query.get(control_id)
    self.assertEqual(
        "321",
        control.custom_attribute_values[0].attribute_value)

  def test_apply_mapping_cad(self):
    """Test apply mapping CAVs proposal."""
    with factories.single_commit():
      control = factories.ControlFactory(title="1")
      cad = factories.CustomAttributeDefinitionFactory(
          definition_type="control",
          attribute_type="Map:Person"
      )
      person = factories.PersonFactory()
      cav = factories.CustomAttributeValueFactory(
          custom_attribute=cad,
          attributable=control,
          attribute_object_id=person.id,
          attribute_value="Person",
      )
    self.assertEqual(person,
                     control.custom_attribute_values[0].attribute_object)
    control_id = control.id
    proposal = factories.ProposalFactory(
        instance=control,
        content={
            "custom_attribute_values": {
                cad.id: {
                    "attribute_value": "Person",
                    "attribute_object": None,
                },
            },
        },
        agenda="agenda content")
    with self.number_obj_revisions_for(control):
      self.apply_proposal(proposal)
    control = all_models.Control.query.get(control_id)
    cav = control.custom_attribute_values[0]
    self.assertEqual("Person", cav.attribute_value)
    self.assertIsNone(cav.attribute_object_id)
