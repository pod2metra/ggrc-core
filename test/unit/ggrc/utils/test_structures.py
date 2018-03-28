# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

import unittest

from ggrc.utils import structures


class TestCaseInsensitiveDict(unittest.TestCase):
    def setUp(self):
        self.ci_dict = structures.CaseInsensitiveDict()

    def test_basic_dict_functions(self):
        self.ci_dict["Hello"] = "World"
        self.assertEqual(self.ci_dict["Hello"], "World")
        self.ci_dict["empty"] = []
        self.assertEqual(self.ci_dict["empty"], [])
        self.ci_dict["EMpTY"].append(56)
        self.assertEqual(self.ci_dict["EmpTy"], [56])

        def get_(dict_, key):
            return dict_[key]

        self.assertRaises(KeyError, get_, self.ci_dict, "non existent key")
        self.assertRaises(KeyError, get_, self.ci_dict, None)

    def test_in_function(self):
        self.ci_dict["Hello"] = "World"
        self.assertTrue("Hello" in self.ci_dict)
        self.assertTrue("hello" in self.ci_dict)
        self.assertTrue("he" not in self.ci_dict)

    def test_items(self):
        """Test that items return sames cases as they were set."""
        self.ci_dict["Hello"] = "World"
        self.ci_dict["HELLO"] = "World"
        self.ci_dict["fOO"] = "bar"

        self.assertEqual(
            sorted(self.ci_dict.items()),
            sorted([("HELLO", "World"), ("fOO", "bar")]))

    def test_lower_items(self):
        """Test that lower_items does not change values."""
        self.ci_dict["Hello"] = "World"
        self.ci_dict["FOO"] = "BAR"

        self.assertEqual(
            sorted(self.ci_dict.lower_items()),
            sorted([("hello", "World"), ("foo", "BAR")]))


class TestCaseInsensitiveDefDict(unittest.TestCase):
    def setUp(self):
        self.ci_dict = structures.CaseInsensitiveDefaultDict(list)

    def test_basic_dict_functions(self):
        self.ci_dict["Hello"] = "World"
        self.assertEqual(self.ci_dict["Hello"], "World")
        self.assertEqual(self.ci_dict["empty"], [])
        self.ci_dict["empty"].append(55)
        self.assertEqual(self.ci_dict["empty"], [55])
        self.ci_dict["EMpTY"].append(56)
        self.assertEqual(self.ci_dict["EmpTy"], [55, 56])

    def test_in_function(self):
        self.ci_dict["Hello"] = "World"
        self.assertTrue("Hello" in self.ci_dict)
        self.assertTrue("hello" in self.ci_dict)
        self.assertTrue("he" not in self.ci_dict)

    def test_items(self):
        """Test that items return sames cases as they were set."""
        self.ci_dict["Hello"] = "World"
        self.ci_dict["HELLO"] = "World"
        self.ci_dict["fOO"] = "bar"

        self.assertEqual(
            sorted(self.ci_dict.items()),
            sorted([("HELLO", "World"), ("fOO", "bar")]))

    def test_lower_items(self):
        """Test that lower_items does not change values."""
        self.ci_dict["Hello"] = "World"
        self.ci_dict["FOO"] = "BAR"

        self.assertEqual(
            sorted(self.ci_dict.lower_items()),
            sorted([("hello", "World"), ("foo", "BAR")]))
