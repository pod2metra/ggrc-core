# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Package contains RBAC related helper functions."""

from ggrc.models import all_models

GA_RNAME = "Administrator"
GE_RNAME = "Editor"
GR_RNAME = "Reader"
GC_RNAME = "Creator"

G_ROLES = {
    r.name: r
    for r in all_models.Role.query.filter(
        all_models.Role.name.in_((GA_RNAME, GE_RNAME, GR_RNAME, GC_RNAME)))
}
