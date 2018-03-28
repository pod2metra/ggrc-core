# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Test Access Control Role validation"""

import unittest
from mock import MagicMock

import ggrc.app  # noqa pylint: disable=unused-import
from ggrc.models import all_models


class TestAccessControlRoles(unittest.TestCase):
    """Test Access Control Role validation"""

    def setUp(self):
        # pylint: disable=protected-access
        self.acr = all_models.AccessControlRole()
        self.acr._get_reserved_names = MagicMock(
            return_value=frozenset({'title'}))
        self.acr._get_global_cad_names = MagicMock(return_value={'reg url': 1})

    def test_simple_validation(self):
        """Test if access control role validation sets the fields correctly"""
        name, object_type = "New Object name", "Control"
        self.acr.name = name
        self.acr.object_type = object_type
        assert self.acr.name == name, \
            "Access control name not properly set {} != {}".format(
                self.acr.name, name)
        assert self.acr.object_type == object_type, \
            "Access control object type not properly set {} != {}".format(
                self.acr.object_type, object_type)

    def test_invalid_name_throws(self):
        """Test if raises on collision with global attributes"""

        with self.assertRaises(ValueError):
            name, object_type = "title", "Control"
            self.acr.name = name
            self.acr.object_type = object_type

    def test_if_invalid_ca_check(self):
        """Test if raises on collision with custom attributes attributes"""
        with self.assertRaises(ValueError):
            name, object_type = "reg url", "Regulation"
            self.acr.name = name
            self.acr.object_type = object_type
