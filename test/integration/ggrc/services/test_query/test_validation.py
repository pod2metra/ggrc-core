# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Integration test for validation posted search query."""

import ddt

from integration.ggrc import TestCase
from integration.ggrc.api_helper import Api


@ddt.ddt
class TestValidation(TestCase):
    """Test validation query."""

    def setUp(self):
        """Log in before performing queries."""
        # we don't call super as TestCase.setUp clears the DB
        # super(BaseQueryAPITestCase, self).setUp()
        self.client.get("/login")
        self.api = Api()

    def assert_validation(self, query_data):
        self.assert400(
            self.api.send_request(
                self.api.client.post, data=query_data, api_link="/query"))

    OPERATIONS = ["=", "!=", "~", "!=", ">", "<", ">=", "<="]

    @ddt.data(*OPERATIONS)
    def test_only_left_validations(self, operation):
        self.assert_validation([{
            "object_name": "Snapshot",
            "filters": {
                "expression": {
                    "left": "title",
                    "op": {
                        "name": operation
                    },
                }
            }
        }])

    @ddt.data(*OPERATIONS)
    def test_only_right_validations(self, operation):
        self.assert_validation([{
            "object_name": "Snapshot",
            "filters": {
                "expression": {
                    "right": "value",
                    "op": {
                        "name": operation
                    },
                }
            }
        }])

    @ddt.data({}, {"name": "x"})
    def test_invalid_operations(self, operation_dict):
        self.assert_validation([{
            "object_name": "Snapshot",
            "filters": {
                "expression": {
                    "right": "value",
                    "op": operation_dict
                }
            }
        }])

    NO_OPERATION_DATA = [{
        "object_name": "Snapshot",
        "filters": {
            "expression": {
                "right": "value",
                "left": "title"
            }
        }
    }]

    NO_OBJECT_NAME_DATA = [{
        "filters": {
            "expression": {
                "left": "title",
                "op": {
                    "name": "="
                }
            }
        }
    }]

    @ddt.data(
        [{}],
        NO_OPERATION_DATA,
        NO_OBJECT_NAME_DATA,
    )
    def test_validation(self, query_data):
        self.assert_validation(query_data)
