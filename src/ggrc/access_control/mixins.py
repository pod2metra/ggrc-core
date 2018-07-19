# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Access Control List model"""

from ggrc import db


class PermissionMixin(object):
  """Permission model mixin."""
  read = db.Column(db.Boolean, nullable=False, default=True)
  update = db.Column(db.Boolean, nullable=False, default=True)
  delete = db.Column(db.Boolean, nullable=False, default=True)
