# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""This module contains AC roles test classes definition."""
from api_search.test_person_filters_complete import generate_classes
from ggrc import db
from ggrc.models import all_models
from ggrc.snapshotter.rules import Types


AC_ROLES = db.session.query(all_models.AccessControlRole.name) \
                     .filter(all_models.AccessControlRole.non_editable) \
                     .distinct()
for ac_role in AC_ROLES:
    generate_classes(Types.all, ac_role[0])
