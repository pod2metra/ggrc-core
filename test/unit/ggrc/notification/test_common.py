# -*- coding: utf-8 -*-

# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Tests for the ggrc.notifications.common module."""

import unittest
from datetime import datetime

from ggrc.notifications.common import sort_comments


class TestSortComments(unittest.TestCase):
    """Tests for the as_user_time() helper function."""

    # pylint: disable=invalid-name

    def test_sorts_comments_inline_newest_first(self):
        """Test that comments data is sorted by creation date (descending)."""
        asmt5_info = (5, "Assessment", "Asmt 5", "www.5.com")

        data = {
            "comment_created": {
                asmt5_info: {
                    12: {
                        "description": "ABCD...",
                        "created_at": datetime(2017, 5, 31, 8, 15, 0)
                    },
                    19: {
                        "description": "All tasks can be closed",
                        "created_at": datetime(2017, 10, 16, 0, 30, 0)
                    },
                    10: {
                        "description": "Comment One",
                        "created_at": datetime(2017, 5, 29, 16, 20, 0)
                    },
                    15: {
                        "description": "I am confused",
                        "created_at": datetime(2017, 8, 15, 11, 13, 0)
                    }
                }
            }
        }

        sort_comments(data)

        comment_data = data["comment_created"].values()[0]
        self.assertIsInstance(comment_data, list)

        descriptions = [c["description"] for c in comment_data]
        expected_descriptions = [
            "All tasks can be closed", "I am confused", "ABCD...",
            "Comment One"
        ]
        self.assertEqual(descriptions, expected_descriptions)
