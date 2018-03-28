# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Test with_memcache util decorator"""

from unittest import TestCase

from ddt import data, ddt, unpack
from appengine import base


@ddt
@base.with_memcache
class TestMemcacheDecorator(TestCase):
    """Test docorator to emulate memcache in test"""

    TESTKEYS = ('1', '2', '3')

    # 2 test required for checking invalidation cache for each test case
    @data(TESTKEYS, TESTKEYS)
    @unpack
    def test_simple(self, *keys):
        """Simple test

    add value in cache
    check it's invalidation on each test"""
        for key in keys:
            self.assertIsNone(self.memcache_client.get(key))
            val = key * 10
            self.memcache_client.add(key, val)
            self.assertEqual(val, self.memcache_client.get(key))
