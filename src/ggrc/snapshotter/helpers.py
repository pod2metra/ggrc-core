# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Various simple helper functions for snapshot generator"""

import collections
from logging import getLogger

from sqlalchemy.sql.expression import tuple_

from ggrc import db
from ggrc import models
from ggrc.snapshotter.datastructures import Stub
from ggrc.snapshotter.datastructures import Pair
from ggrc.utils import benchmark

logger = getLogger(__name__)  # pylint: disable=invalid-name


def get_revisions(pairs, revisions, filters=None):
    """Retrieve revision ids for pairs

  If revisions dictionary is provided it will validate that the selected
  revision exists in the objects revision history.

  Args:
    pairs: set([(parent_1, child_1), (parent_2, child_2), ...])
    revisions: dict({(parent, child): revision_id, ...})
    filters: predicate
  """
    with benchmark("snapshotter.helpers.get_revisions"):
        revision_id_cache = dict()

        if pairs:
            with benchmark("get_revisions.create caches"):
                child_stubs = {pair.child for pair in pairs}

                with benchmark("get_revisions.create child -> parents cache"):
                    parents_cache = collections.defaultdict(set)
                    for parent, child in pairs:
                        parents_cache[child].add(parent)

            with benchmark("get_revisions.retrieve revisions"):
                query = db.session.query(
                    models.Revision.id, models.Revision.resource_type,
                    models.Revision.resource_id).filter(
                        tuple_(models.Revision.resource_type,
                               models.Revision.resource_id)
                        .in_(child_stubs)).order_by(models.Revision.id.desc())
                if filters:
                    for _filter in filters:
                        query = query.filter(_filter)

            with benchmark("get_revisions.create revision_id cache"):
                for revid, restype, resid in query:
                    child = Stub(restype, resid)
                    for parent in parents_cache[child]:
                        key = Pair(parent, child)
                        if key in revisions:
                            if revid == revisions[key]:
                                revision_id_cache[key] = revid
                            else:
                                logger.warning(
                                    "Specified revision for object %s but couldn't find the"
                                    "revision '%s' in object history", key,
                                    revisions[key])
                        else:
                            if key not in revision_id_cache:
                                revision_id_cache[key] = revid
        return revision_id_cache


def get_snapshots(objects=None, ids=None):
    with benchmark("snapshotter.helpers.get_snapshots"):
        if objects and ids:
            raise Exception(
                "Insert only iterable of (parent, child) tuples or set of IDS")
        columns = db.session.query(
            models.Snapshot.id,
            models.Snapshot.context_id,
            models.Snapshot.created_at,
            models.Snapshot.updated_at,
            models.Snapshot.parent_type,
            models.Snapshot.parent_id,
            models.Snapshot.child_type,
            models.Snapshot.child_id,
            models.Snapshot.revision_id,
            models.Snapshot.modified_by_id,
        )
        if objects:
            return columns.filter(
                tuple_(models.Snapshot.parent_type, models.Snapshot.parent_id,
                       models.Snapshot.child_type,
                       models.Snapshot.child_id).in_(
                           {(parent.type, parent.id, child.type, child.id)
                            for parent, child in objects}))
        if ids:
            return columns.filter(models.Snapshot.id.in_(ids))
        return set()


def create_json_stub(model_, context_id, object_id):
    from ggrc.models import all_models
    return {  # pylint: disable=protected-access
        "context_id": context_id,
        "id": object_id,
        "href": "/api/{}/{}".format(
            getattr(all_models, model_)._inflector.table_name,
            object_id),
        "type": model_,
    }


def create_snapshot_dict(pair, revision_id, user_id, context_id):
    """Create dictionary representation of snapshot"""
    parent, child = pair.to_2tuple()
    return {
        "parent_type": parent.type,
        "parent_id": parent.id,
        "child_type": child.type,
        "child_id": child.id,
        "revision_id": revision_id,
        "modified_by_id": user_id,
        "context_id": context_id
    }


def create_snapshot_revision_dict(action, event_id, snapshot, user_id,
                                  context_id):
    """Create dictionary representation of snapshot revision"""
    revision_content = snapshot._asdict()
    metadata = {
        "display_name":
        "Snapshot:{} of {}:{} in {}:{}".format(
            snapshot.id, snapshot.child_type, snapshot.child_id,
            snapshot.parent_type, snapshot.parent_id),
        "modified_by":
        create_json_stub("Person", context_id, user_id),
    }
    revision_content.update(metadata)

    return {
        "action": action,
        "event_id": event_id,
        "content": revision_content,
        "modified_by_id": user_id,
        "resource_id": snapshot[0],
        "resource_type": "Snapshot",
        "context_id": context_id
    }


def create_dry_run_response(pairs, old_revisions, new_revisions):
    with benchmark("create_dry_run_response"):
        response = dict()
        for pair in pairs:
            if pair.parent not in response:
                response[pair.parent] = {}

            old_revision_id = old_revisions.get(pair)
            new_revision_id = new_revisions.get(pair)
            if old_revision_id != new_revision_id:
                response[pair.parent][pair.child] = (old_revision_id,
                                                     new_revision_id)
        return response
