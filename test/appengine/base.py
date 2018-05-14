# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""This module contains utils to activate and deactivate appengine services"""

import functools

from ggrc import settings

from google.appengine.api import memcache
from google.appengine.ext import testbed


def with_memcache(cls):
  """Decorate test class to activativate memcache service"""

  base_setup = cls.setUp
  base_teardown = cls.tearDown

  @functools.wraps(base_setup)
  def setup_decorator(self):
    """Add testbed on setup, activate it and init memcache client"""
    self.testbed = getattr(self, "testbed") or testbed.Testbed()
    # pylint: disable=protected-access
    if not self.testbed._activated:
      self.testbed.activate()
    self.testbed.init_memcache_stub()
    self.memcache_client = memcache.Client()
    try:
      self.saved_memcache_mechanism = settings.MEMCACHE_MECHANISM
      self.setup_memcache_mechanism = True
    except AttributeError:
      self.saved_memcache_mechanism = None
      self.setup_memcache_mechanism = False
    settings.MEMCACHE_MECHANISM = True
    base_setup(self)

  @functools.wraps(base_teardown)
  def teardown_decorator(self):
    """Deactivate testbed"""
    # pylint: disable=protected-access
    if self.testbed._activated:
      self.testbed.deactivate()
    if self.setup_memcache_mechanism:
      settings.MEMCACHE_MECHANISM = self.saved_memcache_mechanism
    base_teardown(self)

  cls.setUp = setup_decorator
  cls.tearDown = teardown_decorator
  return cls
