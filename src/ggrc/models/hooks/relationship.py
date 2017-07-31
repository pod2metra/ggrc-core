# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Relationship creation/modification hooks."""

import sqlalchemy as sa

from ggrc.models import all_models


def init_hook():
  """Initialize Relationship-related hooks."""
  sa.event.listen(all_models.Relationship, "before_insert",
                  all_models.Relationship.validate_attrs)
  sa.event.listen(all_models.Relationship, "before_update",
                  all_models.Relationship.validate_attrs)
