# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"Exceptions definition."


class ElementNotFound(Exception):
    """Raised when an element is not found. Selenium has it's own exception but
 when we're iterating through multiple elements and expect one, we raise our
 own.
 """


class DocstringsMissing(Exception):
    """Since we require for certain classes to have docstrings, we raise this
 exception in case methods are missing them.
 """


class ElementMovingTimeout(Exception):
    """When trying to detect if an element stopped moving so it receives
 click, we usually have timeout for that. If timeout is reached, this
 exception is raised.
 """


class RedirectTimeout(Exception):
    """When detecting if redirect has occurred, we usually check that
 loop isn't infinite and raise this exception if timeout is reached.
 """


class NoClassFound(Exception):
    """Raised in factory in case no class has been found"""
