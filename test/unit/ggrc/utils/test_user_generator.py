# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Unit test suite for utils user_generator."""

import unittest
import mock

from ggrc.utils import user_generator


class TestUserGenerator(unittest.TestCase):
    """Unittests for user generator module."""
    # pylint: disable=invalid-name; test method names are too long for pylint

    @mock.patch('ggrc.settings.EXTERNAL_APP_USER', None)
    def test_is_external_app_user_email_no_setting(self):
        """No EXTERNAL_APP_USER presented in settings."""
        self.assertFalse(
            user_generator.is_external_app_user_email('test@example.com'))

    @mock.patch('ggrc.settings.EXTERNAL_APP_USER', 'some corrupted email')
    def test_is_external_app_user_email_corrupted_email(self):
        """In EXTERNAL_APP_USER is corrupted email."""
        self.assertFalse(
            user_generator.is_external_app_user_email('test@example.com'))

    @mock.patch('ggrc.settings.EXTERNAL_APP_USER',
                'Ext App <test2@example.com>')
    def test_is_external_app_user_email_not_equals(self):
        """EXTERNAL_APP_USER email is not equals to given email."""
        self.assertFalse(
            user_generator.is_external_app_user_email('test@example.com'))

    @mock.patch('ggrc.settings.EXTERNAL_APP_USER',
                'Ext App <test@example.com>')
    def test_is_external_app_user_email_equals(self):
        """EXTERNAL_APP_USER email is equals to given email."""
        self.assertTrue(
            user_generator.is_external_app_user_email('test@example.com'))

    @mock.patch('ggrc.settings.EXTERNAL_APP_USER',
                'Ext App <test@example.com>')
    @mock.patch('ggrc.utils.user_generator.find_user_by_email')
    @mock.patch('ggrc.utils.user_generator.create_user')
    def test_find_or_create_ext_app_user_exists(self, create_user_mock,
                                                find_by_email_mock):
        """External App User exists in database."""
        usr = mock.MagicMock()
        find_by_email_mock.return_value = usr

        self.assertEqual(usr, user_generator.find_or_create_ext_app_user())
        find_by_email_mock.assert_called_once_with('test@example.com')
        create_user_mock.assert_not_called()

    @mock.patch('ggrc.settings.EXTERNAL_APP_USER',
                'Ext App <test@example.com>')
    @mock.patch('ggrc.utils.user_generator.find_user_by_email')
    @mock.patch('ggrc.utils.user_generator.create_user')
    def test_find_or_create_ext_app_user_not_exists(self, create_user_mock,
                                                    find_by_email_mock):
        """External App User doesn't exist in database (creating)."""
        usr = mock.MagicMock()
        find_by_email_mock.return_value = None
        create_user_mock.return_value = usr

        self.assertEqual(usr, user_generator.find_or_create_ext_app_user())
        find_by_email_mock.assert_called_once_with('test@example.com')
        create_user_mock.assert_called_once_with(
            'test@example.com', name='Ext App')
