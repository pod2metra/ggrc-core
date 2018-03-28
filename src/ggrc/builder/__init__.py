# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Resource state representation handlers for GGRC models. Builder modules will
produce specific resource state representations for GGRC models as well as
update/create GGRC model instances from resource state representations.
"""

# pylint: disable=invalid-name


class simple_property(property):
    pass


class callable_property(property):
    pass
