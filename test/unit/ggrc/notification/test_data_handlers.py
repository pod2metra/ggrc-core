# -*- coding: utf-8 -*-

# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Tests for the ggrc.notifications.notification_handlers module."""

from datetime import datetime
import unittest
import mock

import ddt

from ggrc.notifications import data_handlers


@ddt.ddt
class TestAsUserTime(unittest.TestCase):
    """Tests for the as_user_time() helper function."""

    # pylint: disable=invalid-name

    def test_converting_dst_timestamp(self):
        """Test converting timestamps in daylight saving time part of the year."""
        timestamp = datetime(2017, 6, 13, 15, 40, 37)
        result = data_handlers.as_user_time(timestamp)
        self.assertEqual(result, "06/13/2017 08:40:37 PDT")

    def test_converting_non_dst_timestamp(self):
        """Test converting timestamps in non-daylight saving time part of the year.
    """
        timestamp = datetime(2017, 2, 13, 15, 40, 37)
        result = data_handlers.as_user_time(timestamp)
        self.assertEqual(result, "02/13/2017 07:40:37 PST")

    @ddt.data(
        {
            "role_ids": [1, 2, 3],
            "new_acl": [{
                "ac_role_id": 1,
                "person_id": 1
            }, {
                "ac_role_id": 2,
                "person_id": 2
            }, {
                "ac_role_id": 3,
                "person_id": 3
            }],
            "old_acl": [{
                "ac_role_id": 1,
                "person_id": 1
            }, {
                "ac_role_id": 2,
                "person_id": 2
            }, {
                "ac_role_id": 3,
                "person_id": 3
            }],
            "expected_role_ids": [],
        },
        {
            "role_ids": [1, 2, 3, 4, 5],
            "new_acl": [{
                "ac_role_id": 1,
                "person_id": 1
            }, {
                "ac_role_id": 2,
                "person_id": 2
            }, {
                "ac_role_id": 3,
                "person_id": 3
            }],
            "old_acl": [{
                "ac_role_id": 1,
                "person_id": 1
            }, {
                "ac_role_id": 2,
                "person_id": 2
            }, {
                "ac_role_id": 3,
                "person_id": 3
            }],
            "expected_role_ids": [],
        },
        {
            "role_ids": [1],
            "new_acl": [{
                "ac_role_id": 1,
                "person_id": 1
            }, {
                "ac_role_id": 2,
                "person_id": 2
            }, {
                "ac_role_id": 3,
                "person_id": 3
            }],
            "old_acl": [{
                "ac_role_id": 1,
                "person_id": 1
            }, {
                "ac_role_id": 2,
                "person_id": 2
            }, {
                "ac_role_id": 3,
                "person_id": 3
            }],
            "expected_role_ids": [],
        },
        {
            "role_ids": [1],
            "new_acl": [{
                "ac_role_id": 1,
                "person_id": 1
            }, {
                "ac_role_id": 2,
                "person_id": 2
            }, {
                "ac_role_id": 3,
                "person_id": 3
            }],
            "old_acl": [],
            "expected_role_ids": [1],
        },
        {
            "role_ids": [1],
            "new_acl": [],
            "old_acl": [{
                "ac_role_id": 1,
                "person_id": 1
            }, {
                "ac_role_id": 2,
                "person_id": 2
            }, {
                "ac_role_id": 3,
                "person_id": 3
            }],
            "expected_role_ids": [1],
        },
        {
            "role_ids": [1, 2, 3],
            "new_acl": [{
                "ac_role_id": 1,
                "person_id": 1
            }, {
                "ac_role_id": 2,
                "person_id": 2
            }, {
                "ac_role_id": 3,
                "person_id": 3
            }],
            "old_acl": [],
            "expected_role_ids": [1, 2, 3],
        },
        {
            "role_ids": [1, 2, 3],
            "new_acl": [],
            "old_acl": [{
                "ac_role_id": 1,
                "person_id": 1
            }, {
                "ac_role_id": 2,
                "person_id": 2
            }, {
                "ac_role_id": 3,
                "person_id": 3
            }],
            "expected_role_ids": [1, 2, 3],
        },
        {
            "role_ids": [1],
            "new_acl": [{
                "ac_role_id": 1,
                "person_id": 4
            }, {
                "ac_role_id": 2,
                "person_id": 5
            }, {
                "ac_role_id": 3,
                "person_id": 6
            }],
            "old_acl": [{
                "ac_role_id": 1,
                "person_id": 1
            }, {
                "ac_role_id": 2,
                "person_id": 2
            }, {
                "ac_role_id": 3,
                "person_id": 3
            }],
            "expected_role_ids": [1],
        },
    )
    @ddt.unpack
    def test_get_updated_roles(self, role_ids, new_acl, old_acl,
                               expected_role_ids):
        """Get updated roles geenrator call."""
        roles = {r_id: mock.Mock() for r_id in role_ids}
        expected_role = {roles[i] for i in expected_role_ids}
        # pylint: disable=protected-access
        self.assertEqual(expected_role,
                         data_handlers._get_updated_roles(
                             new_acl, old_acl, roles))
