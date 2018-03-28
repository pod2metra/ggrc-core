# -*- coding: utf-8 -*-

# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Tests for the ggrc.notifications.notification_handlers module."""

import unittest

from ggrc.notifications.notification_handlers import _align_by_ids, IdValPair


class TestAlignByIds(unittest.TestCase):
    """Tests for the _align_by_ids helper function."""

    # pylint: disable=invalid-name

    def test_yields_nothing_for_empty_iterables(self):
        """Giving two empty iterables should result in no pairs yielded."""
        result = list(_align_by_ids([], []))
        self.assertFalse(result)

    def test_yields_item_pairs_with_same_ids(self):
        """Items in yielded pairs shoučld be matched by their IDs."""
        seq = [
            IdValPair(8, "foo"),
            IdValPair(3, "bar"),
            IdValPair(7, "baz"),
            IdValPair(9, "qux"),
        ]

        # values scrambled to test that items are indeed matched by their IDs
        seq2 = [
            IdValPair(7, "qux"),
            IdValPair(3, "bar"),
            IdValPair(9, "foo"),
            IdValPair(8, "baz"),
        ]

        result = list(_align_by_ids(seq, seq2))
        for item, item2 in result:
            self.assertEqual(item.id, item2.id)

    def test_pairs_items_with_no_match_with_none(self):
        """Items without a matching ID are paired with None when yielded."""
        seq = [
            IdValPair(9, "bar"),
        ]
        seq2 = [
            IdValPair(5, "foo"),
            IdValPair(3, "moo"),
        ]

        result = list(_align_by_ids(seq, seq2))
        expected = [
            (IdValPair(9, "bar"), None),
            (None, IdValPair(5, "foo")),
            (None, IdValPair(3, "moo")),
        ]

        self.assertItemsEqual(result, expected)
