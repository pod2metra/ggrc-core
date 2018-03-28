# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Tests for owned operator."""

import ddt

from integration.ggrc import TestCase
from integration.ggrc.query_helper import WithQueryApi
from integration.ggrc.models import factories


@ddt.ddt
class TestOwned(TestCase, WithQueryApi):
    """Test for correct working operator owned"""

    def setUp(self):
        super(TestOwned, self).setUp()
        self.client.get("/login")
        with factories.single_commit():
            self.person = factories.PersonFactory()
            self.control = factories.ControlFactory()

    @ddt.data(
        ((True, True), True),
        ((True, False), True),
        ((False, True), True),
        ((False, False), False),
    )
    @ddt.unpack
    def test_acl_people(self, my_work_flags, should_return):
        """Owned returns objects where person has role with my_work set."""
        with factories.single_commit():
            for my_work in my_work_flags:
                role = factories.AccessControlRoleFactory(
                    object_type="Control", my_work=my_work)
                factories.AccessControlListFactory(
                    ac_role=role,
                    person=self.person,
                    object=self.control,
                )

        control_id = self.control.id

        ids = self._get_first_result_set({
            "object_name": "Control",
            "type": "ids",
            "filters": {
                "expression": {
                    "object_name": "Person",
                    "op": {
                        "name": "owned"
                    },
                    "ids": [self.person.id]
                }
            }
        }, "Control", "ids")

        if should_return:
            self.assertEqual(ids, [control_id])
        else:
            self.assertEqual(ids, [])
