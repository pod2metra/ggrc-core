# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Tests for the CommentColumnHandler class"""

import unittest

import ddt

from ggrc.converters.handlers.comments import CommentColumnHandler


@ddt.ddt
class CommentColumnHandlerTestCase(unittest.TestCase):
    """Base class for DateColumnHandler tests"""

    @ddt.data((";;;;", []), (" ;; ", []), (" ;; ;; ", []), (" ", []), ("", []),
              ("a;b", ["a;b"]), ("a;;b", ["a", "b"]), ("a;;;b", ["a;", "b"]),
              ("a;;;;b", ["a", "b"]), ("a;;;;;b", ["a;", "b"]),
              (" a;; ;;b ", ["a", "b"]))
    @ddt.unpack
    def test_split_comments(self, raw_value, expected_result):
        """Test splitting of comments"""
        result = CommentColumnHandler.split_comments(raw_value)
        self.assertEqual(result, expected_result)
