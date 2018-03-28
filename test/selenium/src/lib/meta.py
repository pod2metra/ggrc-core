# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Metaclasses module"""

import pytest

from lib import exception, constants, environment


class DecorateFlakyTests(type):
    # todo: this should be refactored to DecorateMethods and used with a
    # factory
    """Decorates all test methods with decorator that repeats failed test
 couple of times
 """

    def __new__(mcs, name, bases, dct):
        for attr_name, value in dct.items():
            if any([
                    method_name in attr_name for method_name in [
                        constants.test_runner.TEST_METHOD_PREFIX,
                        constants.test_runner.TEST_METHOD_POSTFIX
                    ]
            ]) and callable(value):
                dct[attr_name] = pytest.mark.flaky(
                    reruns=environment.RERUN_FAILED_TEST)(value)

        return super(DecorateFlakyTests, mcs).__new__(mcs, name, bases, dct)


class RequireDocs(type):
    """Requires from all methods to include docstrings"""

    def __new__(mcs, name, bases, dct):
        for attr_name, value in dct.items():
            if callable(value) and not hasattr(value, "__doc__"):
                raise exception.DocstringsMissing(attr_name)

        return super(RequireDocs, mcs).__new__(mcs, name, bases, dct)
