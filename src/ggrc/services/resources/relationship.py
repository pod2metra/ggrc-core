# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Custom Resource for Relationship that creates Snapshots when needed.

When Audit-Snapshottable Relationship is POSTed, a Snapshot should be created
instead.
"""

from ggrc.builder import json as json_builder
from ggrc import db
import ggrc.services.common
from ggrc.models.snapshot import Snapshot
from ggrc.login import get_current_user


class RelationshipResource(ggrc.services.common.Resource):
    """Custom Resource that transforms Relationships to Snapshots on un-json."""

    # pylint: disable=abstract-method

    @staticmethod
    def _parse_snapshot_data(src):
        """Try to find parent-child pair from src.

    Args:
      src: source JSON from which a Relationship would have been created.

    Returns:
      (parent, child, is_snapshot):
          (source, destination, True) if source is a Parent and destination is
          a Snapshottable;
          (destination, source, True) if source is a Snapshottable and
          destination is a Parent;
          (None, None, False) otherwise.
    """
        from ggrc.snapshotter import rules as snapshot_rules
        parent, child = None, None
        if src["source"]["type"] in snapshot_rules.Types.parents:
            parent, child = src["source"], src["destination"]
        elif src["destination"]["type"] in snapshot_rules.Types.parents:
            parent, child = src["destination"], src["source"]

        is_snapshot = bool(
            parent) and child["type"] in snapshot_rules.Types.all
        return parent, child, is_snapshot

    def _get_model_instance(self, src=None, body=None):
        """For Parent and Snapshottable src and dst, create an empty Snapshot."""
        _, _, is_snapshot = self._parse_snapshot_data(src)

        if is_snapshot:
            obj = Snapshot()
            db.session.add(obj)
            return obj
        else:
            return super(RelationshipResource, self)._get_model_instance(
                src, body)

    def json_create(self, obj, src):
        """For Parent and Snapshottable src and dst, fill in the Snapshot obj."""
        parent, child, is_snapshot = self._parse_snapshot_data(src)

        if is_snapshot:
            snapshot_data = {
                "parent": parent,
                "child_type": child["type"],
                "child_id": child["id"],
                "update_revision": "new",
            }
            json_builder.create(obj, snapshot_data)
            obj.modified_by = get_current_user()
            obj.context = obj.parent.context
        else:
            return super(RelationshipResource, self).json_create(obj, src)
