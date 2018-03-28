# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""AccessControlList creation hooks."""
from collections import defaultdict

from ggrc.access_control.role import get_custom_roles_for
from ggrc.models import all_models
from ggrc.models.hooks.relationship import create_related_roles, related, \
    add_related_snapshots
from ggrc.models.mixins.assignable import Assignable
from ggrc.models.relationship import Stub, RelationshipsCache


def collect_snapshot_ids(related_objects):
    """Collect snapshot ids related to base assigned object

  Args:
    related_objects: Dict of base objects with set of related Stubs

  Returns:
    Dict of related ids and base Stub
  """
    snapshot_ids = {}
    for base_stub, related_stubs in related_objects.items():
        for related_stub in related_stubs:
            if related_stub.type == "Snapshot":
                snapshot_ids[related_stub.id] = base_stub
    return snapshot_ids


def handle_acl_creation(session):
    """Create relations for mapped objects."""
    base_objects = defaultdict(set)
    for obj in session.new:
        if isinstance(obj, all_models.AccessControlList):
            acr_id = obj.ac_role.id if obj.ac_role else obj.ac_role_id
            acr_name = get_custom_roles_for(obj.object_type).get(acr_id)
            if acr_name in Assignable.ASSIGNEE_TYPES:
                base_objects[Stub(obj.object_type, obj.object_id)].add(obj)
    if base_objects:
        related_objects = related(base_objects.keys(), RelationshipsCache())
        snapshot_ids = collect_snapshot_ids(related_objects)
        if snapshot_ids:
            add_related_snapshots(snapshot_ids, related_objects)
        create_related_roles(base_objects, related_objects)
