# -*- coding: utf-8 -*-

# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Tests for the DateColumnHandler class"""

import unittest
from mock import MagicMock

from ggrc.converters.handlers.handlers import DateColumnHandler


class DateColumnHandlerTestCase(unittest.TestCase):
    """Base class for DateColumnHandler tests"""

    def setUp(self):
        row_converter = MagicMock(name=u"row_converter")
        key = u"field_foo"
        self.handler = DateColumnHandler(row_converter, key)


class ParseItemTestCase(DateColumnHandlerTestCase):
    """Tests for the parse_item() method"""

    # pylint: disable=invalid-name

    def test_returns_none_for_empty_strings(self):
        """The method should return None if given an empty string."""
        self.handler.raw_value = u""
        result = self.handler.parse_item()
        self.assertIsNone(result)

    def test_returns_none_for_whitespace_only_strings(self):
        """The method should return None if given a whitespace-only string."""
        self.handler.raw_value = u" \t\n  \n\t \r\n \t  "
        result = self.handler.parse_item()
        self.assertIsNone(result)
