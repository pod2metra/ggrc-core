# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Tests for IN operator."""

import ddt

from integration.ggrc import TestCase
from integration.ggrc.query_helper import WithQueryApi
from integration.ggrc.models import factories


@ddt.ddt
class TestIn(TestCase, WithQueryApi):
    """Test suite for IN operator."""

    def setUp(self):
        super(TestIn, self).setUp()
        self.client.get("/login")
        test_objects = []
        with factories.single_commit():
            test_objects.append(factories.ControlFactory(title="c1"))
            test_objects.append(factories.ControlFactory(title="c2"))
            test_objects.append(
                factories.ControlFactory(title="c3", status="Active"))

        self.title_id_map = {ob.title: ob.id for ob in test_objects}

    @ddt.data(("Control", "status", ["Draft"], ["c1", "c2"]),
              ("Control", "title", ["c1", "c2"], ["c1", "c2"]),
              ("Control", "title", [], []),
              ("Control", "status", ["Fake_status"], []),
              ("Control", "title", ["c1", "c"], ["c1"]))
    def test_in_operator(self, (object_type, field, values, expected_titles)):
        """IN operator works for string fields."""

        expected_ids = [self.title_id_map[title] for title in expected_titles]

        result = self._get_first_result_set(
            self._make_query_dict(
                object_type, expression=[field, "IN", values], type_="ids"),
            object_type,
            "ids",
        )
        self.assertItemsEqual(result, expected_ids)
