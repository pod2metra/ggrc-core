# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Test Administrator permissions."""

from ggrc.models import all_models
from integration.ggrc import TestCase
from integration.ggrc import generator
from integration.ggrc.models import factories


class TestAdminRole(TestCase):
    """Test suite to check Admin role logic."""

    def setUp(self):
        self.generator = generator.ObjectGenerator()
        with factories.single_commit():
            self.new_user = factories.PersonFactory()
            self.admin_role = (
                all_models.Role.query.filter_by(name="Administrator").one())

    def test_admin_context(self):
        """Admin UserRole gets context_id=0 from a stub."""
        self.generator.generate_object(
            all_models.UserRole,
            data={
                "person": self.generator.create_stub(self.new_user),
                "role": self.generator.create_stub(self.admin_role),
                "context": {
                    "type": "Context",
                    "id": 0
                },
            })

        user_role = all_models.UserRole.query.filter_by(
            person_id=self.new_user.id, ).one()
        self.assertEqual(user_role.context_id, 0)
