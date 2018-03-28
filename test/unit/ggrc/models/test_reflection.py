# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Unit tests for reflections module."""

import unittest

from ggrc.models.reflection import AttributeInfo


class TestAttributeInfo(unittest.TestCase):
    """Unit tests for AttributeInfo class."""

    def test_gather_aliases(self):
        """Test gather all aliases."""

        class Child(object):
            # pylint: disable=too-few-public-methods
            _aliases = {
                "child_normal": "normal",
                "child_extended": {
                    "display_name": "Extended",
                },
                "child_filter_only": {
                    "display_name": "Extended",
                    "filter_only": True,
                },
            }

        class Parent(Child):
            # pylint: disable=too-few-public-methods
            _aliases = {
                "parent_normal": "normal",
                "parent_extended": {
                    "display_name": "Extended",
                },
                "parent_filter_only": {
                    "display_name": "Extended",
                    "filter_only": True,
                },
            }

        self.assertEqual(
            AttributeInfo.gather_aliases(Parent), {
                "parent_normal": "normal",
                "parent_extended": {
                    "display_name": "Extended",
                },
                "parent_filter_only": {
                    "display_name": "Extended",
                    "filter_only": True,
                },
                "child_normal": "normal",
                "child_extended": {
                    "display_name": "Extended",
                },
                "child_filter_only": {
                    "display_name": "Extended",
                    "filter_only": True,
                },
            })

    def test_gather_visible_aliases(self):
        """Test gather visible aliases."""

        class Child(object):
            # pylint: disable=too-few-public-methods
            _aliases = {
                "visible_child_normal": "normal",
                "visible_child_extended": {
                    "display_name": "Extended",
                },
                "child_filter_only": {
                    "display_name": "Extended",
                    "filter_only": True,
                },
            }

        class Parent(Child):
            # pylint: disable=too-few-public-methods
            _aliases = {
                "visible_parent_normal": "normal",
                "visible_parent_extended": {
                    "display_name": "Extended",
                },
                "parent_filter_only": {
                    "display_name": "Extended",
                    "filter_only": True,
                },
            }

        self.assertEqual(
            AttributeInfo.gather_visible_aliases(Parent), {
                "visible_parent_normal": "normal",
                "visible_parent_extended": {
                    "display_name": "Extended",
                },
                "visible_child_normal": "normal",
                "visible_child_extended": {
                    "display_name": "Extended",
                },
            })
