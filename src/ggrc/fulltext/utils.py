# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Utils module for fulltext app part."""

from ggrc.fulltext import mixin


def get_property_tmpl(obj):
  if isinstance(obj, mixin.Indexed):
    return obj.PROPERTY_TEMPLATE
  else:
    return u"{}"
