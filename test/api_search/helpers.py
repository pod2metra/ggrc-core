# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""This module contains helper functions for working with api search tests."""

import uuid
from collections import namedtuple

from api_search.setters import AC_ROLES, CAD_PERSON_TITLE
from ggrc.fulltext import get_indexer
from ggrc.models import all_models
from ggrc.snapshotter.indexer import reindex_snapshots
from ggrc.snapshotter.rules import Types
from integration.ggrc import TestCase
from integration.ggrc.models import factories


def create_reindexed_snapshots(audit_id, objects):
    """Create snapshots for list of provided objects and reindex them"""
    # pylint: disable=protected-access
    snapshottable_objects = [o for o in objects if o.type in Types.all]
    audit = all_models.Audit.query.get(audit_id)
    snapshots = TestCase._create_snapshots(audit, snapshottable_objects)
    reindex_snapshots_ids = [snap.id for snap in snapshots]
    get_indexer().delete_records_by_ids(
        "Snapshot", reindex_snapshots_ids, commit=False)
    reindex_snapshots(reindex_snapshots_ids)


def create_tuple_data(obj_id, searchable, subprops):
    """Create tuple with expected object id and subproperties of
  searchable object"""
    expected = namedtuple("expected_row", "props id")
    if searchable:
        subprop_vals = [getattr(searchable, sp) for sp in subprops]
        property_vals = namedtuple("property_vals", " ".join(subprops))
        expected.props = property_vals(*subprop_vals)
    else:
        expected.props = []
    expected.id = obj_id
    return expected


def create_rand_person():
    """Create user with random username, name and email"""
    user_name = uuid.uuid1()
    return factories.PersonFactory(
        # Make User Name different from Name
        name="User {}".format(user_name),
        email="{}@example.com".format(user_name))


def field_exists(model, field):
    """Check if field exists for provided model"""
    return hasattr(model, field) or \
        field in AC_ROLES[model.__name__] or \
        field == CAD_PERSON_TITLE
