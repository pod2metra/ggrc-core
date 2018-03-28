# -*- coding: utf-8 -*-

# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Tests for functions in the ggrc.utils module."""

import os
import unittest

from mock import patch

from ggrc.utils import get_url_root
from ggrc.settings import default


class TestGetUrlRoot(unittest.TestCase):
    """Test suite for the get_url_root() function."""

    # pylint: disable=invalid-name

    def test_using_request_url_when_custom_url_root_setting_undefined(self):
        """Url root should be read from request if not set in environment."""
        with patch("ggrc.utils.CUSTOM_URL_ROOT", None):
            with patch("ggrc.utils.request") as fake_request:
                fake_request.url_root = "http://www.foo.com/"
                result = get_url_root()

        self.assertEqual(result, "http://www.foo.com/")

    def test_using_request_url_when_custom_url_root_setting_empty_string(self):
        """Url root should be read from request if set to empty string in environ.
    """
        with patch("ggrc.utils.CUSTOM_URL_ROOT", ""):
            with patch("ggrc.utils.request") as fake_request:
                fake_request.url_root = "http://www.foo.com/"
                result = get_url_root()

        self.assertEqual(result, "http://www.foo.com/")

    def test_using_custom_url_root_setting_if_defined(self):
        """Url root should be read from environment if defined there."""
        with patch("ggrc.utils.CUSTOM_URL_ROOT",
                   "http://www.default-root.com/"):
            with patch("ggrc.utils.request") as fake_request:
                fake_request.url_root = "http://www.foo.com/"
                result = get_url_root()

        self.assertEqual(result, "http://www.default-root.com/")


class TestSettings(unittest.TestCase):
    """Test loading settings from environment."""

    @patch.dict(os.environ, {})
    def test_default_values(self):
        """Test loading default values variable."""
        reload(default)  # Need to reload for variable reinitialization.
        self.assertEqual(default.COMPANY, "Company, Inc.")
        self.assertEqual(default.COMPANY_LOGO_TEXT, "Company")

    @patch.dict(os.environ, {
        "COMPANY": "TestCompany",
        "COMPANY_LOGO_TEXT": "TestCompanyLogo",
    })
    def test_loading_vars_from_env(self):
        """Test loading settings variables from environment."""
        reload(default)  # Need to reload for variable reinitialization.
        self.assertEqual(default.COMPANY, "TestCompany")
        self.assertEqual(default.COMPANY_LOGO_TEXT, "TestCompanyLogo")
