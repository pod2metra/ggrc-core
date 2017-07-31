# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Decorators."""
# pylint: disable=protected-access

import logging
import time
from functools import wraps

from lib import constants, environment, exception, file_ops
from lib.utils import selenium_utils

LOGGER = logging.getLogger(__name__)


def take_screenshot_on_error(fun):
  """Decorate method and make screenshot on any exception."""
  # todo: replace with pytest-selenium which automagically takes
  def wrapper(self, *args):
    "Wrapper."
    try:
      return fun(self, *args)
    except Exception as exception:
      LOGGER.error(exception)
      file_path = (environment.LOG_PATH + self.__class__.__name__ + "." +
                   self._driver.title)
      unique_file_path = file_ops.get_unique_postfix(file_path, ".png")
      self._driver.get_screenshot_as_file(unique_file_path)
      raise
  return wrapper


def wait_for_redirect(fun):
  """Decorates methods and wait until URL has changed."""
  @wraps(fun)
  def wrapper(self, *args, **kwargs):
    "Wrapper."
    from_url = self._driver.current_url
    result = fun(self, *args, **kwargs)
    timer_start = time.time()
    while from_url == self._driver.current_url:
      time.sleep(0.1)
      if time.time() - timer_start > constants.ux.MAX_USER_WAIT_SECONDS:
        raise exception.RedirectTimeout(
            "Failed to redirect from {} to {}".format(
                from_url, self._driver.current_url))
    return result
  return wrapper


def handle_alert(fun):
  """Accept or dismiss alert."""
  @wraps(fun)
  def wrapper(self, *args, **kwargs):
    "Wrapper."
    result = fun(self, *args, **kwargs)
    selenium_utils.handle_alert(self._driver, accept=True)
    return result
  return wrapper


def lazy_property(fun):
  """Decorator for lazy initialization of property."""
  prop_name = "_lazy_" + fun.__name__

  @property
  def lazy(self):
    """Check if property exist in object, if no setattr"""
    if not hasattr(self, prop_name):
      setattr(self, prop_name, fun(self))
    return getattr(self, prop_name)
  return lazy
