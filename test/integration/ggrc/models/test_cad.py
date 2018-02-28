# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Test for cad api."""

import ddt

from ggrc.models import all_models

from integration.ggrc import TestCase
from integration.ggrc.models import factories
from integration.ggrc.api_helper import Api


@ddt.ddt
class TestCAD(TestCase):

  def setUp(self):
    super(TestCAD, self).setUp()
    self.api = Api()
    self.client.get("/login")

  @ddt.data(True, False)
  def test_delete_permissions(self, flag):
    """Check delete cad allowed if is_delete_allowed is {0}"""
    resp = self.api.delete(
        factories.CustomAttributeDefinitionFactory(
            title="test",
            is_delete_allowed=flag,
            definition_type="control"
        )
    )
    self.assertEqual(200 if flag else 403, resp.status_code)

  def test_delete_flag_setup(self):
    """Check is_delete_allowed value for CAD."""
    with factories.single_commit():
      control = factories.ControlFactory(title="1")
      cad = factories.CustomAttributeDefinitionFactory(
          title="test",
          definition_type="control")
    cad = all_models.CustomAttributeDefinition.query.get(cad.id)
    self.assertTrue(cad.is_delete_allowed)
    factories.CustomAttributeValueFactory(
        custom_attribute=cad,
        attributable=control,
        attribute_value="Test",
    )
    cad = all_models.CustomAttributeDefinition.query.get(cad.id)
    self.assertFalse(cad.is_delete_allowed)
