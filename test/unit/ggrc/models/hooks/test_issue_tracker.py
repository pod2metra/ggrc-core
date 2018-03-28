# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Test issue_tracker hooks."""

import unittest

import ddt
import mock

from ggrc.models.hooks import issue_tracker


@ddt.ddt
class TestUtilityFunctions(unittest.TestCase):
    """Test utility function in issue_tracker module."""

    def setUp(self):
        super(TestUtilityFunctions, self).setUp()
        self.session = mock.MagicMock()

    @ddt.data(
        (
            {
                'component_id': '1111',
                'hotlist_id': '2222'
            },
            None,
        ),
        (
            {
                'component_id': '1111'
            },
            None,
        ),
        (
            {
                'hotlist_id': '2222'
            },
            None,
        ),
        (
            {
                'component_id': 'zzz'
            },
            issue_tracker.exceptions.ValidationError,
        ),
        (
            {
                'hotlist_id': 'zzz'
            },
            issue_tracker.exceptions.ValidationError,
        ),
    )
    @ddt.unpack
    def test_validate_info(self, info, expected_error):
        """Test _validate_issue_tracker_info function."""
        initial_info = dict(info)
        # pylint: disable=protected-access
        if expected_error:
            with self.assertRaises(expected_error):
                issue_tracker._validate_issue_tracker_info(info)
        else:
            issue_tracker._validate_issue_tracker_info(info)

        self.assertEqual(info, initial_info)

    @ddt.data(
        (
            {
                'component_id': '1111',
                'hotlist_id': '2222'
            },
            {
                'component_id': 1111,
                'hotlist_id': 2222
            },
            None,
        ),
        (
            {
                'component_id': '1111'
            },
            {
                'component_id': 1111
            },
            None,
        ),
        (
            {
                'hotlist_id': '2222'
            },
            {
                'hotlist_id': 2222
            },
            None,
        ),
        (
            {
                'component_id': 'zzz'
            },
            None,
            issue_tracker.exceptions.ValidationError,
        ),
        (
            {
                'hotlist_id': 'zzz'
            },
            None,
            issue_tracker.exceptions.ValidationError,
        ),
    )
    @ddt.unpack
    def test_normalize_info(self, info, expected, expected_error):
        """Test _normalize_issue_tracker_info function."""
        # pylint: disable=protected-access
        if expected_error:
            with self.assertRaises(expected_error):
                issue_tracker._normalize_issue_tracker_info(info)
        else:
            issue_tracker._normalize_issue_tracker_info(info)
            self.assertEqual(info, expected)
