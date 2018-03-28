# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Test should_receive function in the notifications.common module
"""

import unittest
from mock import Mock

from ggrc.notifications.common import should_receive


class TestShouldReceive(unittest.TestCase):
    """Test should_receive function"""

    def setUp(self):
        self.notif = Mock(id=1)
        self.no_access_person = Mock(system_wide_role="No Access")
        self.default_digest_person = Mock(
            system_wide_role="Reader", notification_configs=[])
        self.enabled_digest_person = Mock(
            system_wide_role="Reader",
            notification_configs=[
                Mock(enable_flag=True, notif_type="Email_Digest")
            ])
        self.disabled_digest_person = Mock(
            system_wide_role="Reader",
            notification_configs=[
                Mock(enable_flag=False, notif_type="Email_Digest")
            ])

    def _call_should_receive(self, person, force_notifications):
        """Helper function that calls should_receive and returns it's result"""
        if person is None:
            user_id = -1
            user_cache = {}
        else:
            user_id = 1
            user_cache = {user_id: person}
        user_data = {
            "force_notifications": {
                1: force_notifications
            },
            "user": {
                "id": user_id
            }
        }
        return should_receive(self.notif, user_data, user_cache)

    def test_invalid_user(self):
        """should_receive returns False when user is invalid"""
        res = self._call_should_receive(None, True)
        self.assertFalse(res)

    def test_no_access_user(self):
        """should_receive returns False when user has No Access"""
        res = self._call_should_receive(self.no_access_person, True)
        self.assertFalse(res)

    def test_default_email_digest(self):
        """should_receive returns True when notification_configs not set"""
        res = self._call_should_receive(self.default_digest_person, False)
        self.assertTrue(res)

    def test_enabled_email_digest_flag(self):
        """should_receive returns True when email_digest flag enabled"""
        res = self._call_should_receive(self.enabled_digest_person, False)
        self.assertTrue(res)

    def test_disabled_email_digest_flag(self):
        """should_receive returns False when email_digest flag disabled"""
        res = self._call_should_receive(self.disabled_digest_person, False)
        self.assertFalse(res)

    def test_force_notifications(self):
        """should_receive returns True when force_notif is set"""
        res = self._call_should_receive(self.disabled_digest_person, True)
        self.assertTrue(res)
