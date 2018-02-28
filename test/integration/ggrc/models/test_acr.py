# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Test for acr api."""

import ddt

from ggrc.models import all_models

from integration.ggrc import TestCase
from integration.ggrc.models import factories
from integration.ggrc.api_helper import Api


@ddt.ddt
class TestACR(TestCase):

  def setUp(self):
    super(TestACR, self).setUp()
    self.api = Api()
    self.client.get("/login")

  @ddt.data(True, False)
  def test_delete_permissions(self, flag):
    """Check delete acr allowed if is_delete_allowed is {0}"""
    resp = self.api.delete(
        factories.AccessControlRoleFactory(name="role", is_delete_allowed=flag)
    )
    self.assertEqual(200 if flag else 403, resp.status_code)

  def test_delete_flag_setup(self):
    """Check is_delete_allowed value for ACR."""
    with factories.single_commit():
      control = factories.ControlFactory(title="1")
      role = factories.AccessControlRoleFactory(
          object_type=control.type, name="role")
      person = factories.PersonFactory()
    role = all_models.AccessControlRole.query.get(role.id)
    self.assertTrue(role.is_delete_allowed)
    factories.AccessControlListFactory(
        person=person,
        ac_role=role,
        object=control,
    )
    role = all_models.AccessControlRole.query.get(role.id)
    self.assertFalse(role.is_delete_allowed)
