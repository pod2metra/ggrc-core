# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Utility class for handling revisions."""

from logging import getLogger

from sqlalchemy.sql import select
from sqlalchemy import func
from sqlalchemy import literal

from ggrc import db
from ggrc.utils import benchmark
from ggrc.login import get_current_user_id
from ggrc.models import all_models
from ggrc.snapshotter.rules import Types

logger = getLogger(__name__)  # pylint: disable=invalid-name


def get_revisions_by_type(type_):
    """Get latest revisions for all existing objects

  Args:
    type_ (str): the resource_type of revisions to fetch.

  Returns:
    dict with object_id as key and revision_id of the latest revision as value.
  """

    revisions = db.session.execute("""
      SELECT * FROM (
          SELECT id, resource_id
          FROM revisions
          WHERE resource_type = :type
          ORDER BY resource_id, id DESC
      ) AS revs
      GROUP BY resource_id
      """, [{
        "type": type_
    }])

    return {row.resource_id: row.id for row in revisions}


def _fix_type_revisions(event, type_, obj_rev_map):
    """Update revision content for all rows of a given model type."""
    model = getattr(all_models, type_, None)
    revisions_table = all_models.Revision.__table__
    if not model:
        logger.warning("Failed to update revisions for invalid model: %s",
                       type_)
        return

    if not hasattr(model, "log_json"):
        logger.warning(
            "Model '%s' has no log_json method, revision generation "
            "skipped", type_)
        return

    chunk = 1000
    all_objects = model.eager_query().order_by(model.id)
    all_objects_count = model.query.count()

    for i in range(all_objects_count // chunk + 1):
        objects_chunk = all_objects.limit(chunk).offset(i * chunk)
        chunk_with_revisions = [
            obj for obj in objects_chunk if obj.id in obj_rev_map
        ]
        chunk_without_revisions = [
            obj for obj in objects_chunk if obj.id not in obj_rev_map
        ]

        # 1. Update the object's latest revision using the value of the up to date
        # log_json function
        _update_existing_revisions(chunk_with_revisions, revisions_table,
                                   obj_rev_map)

        # 2. For each unlogged object log a "created"/"modified" revision with
        # content equal to obj.log_json()
        _recover_create_revisions(revisions_table, event, type_,
                                  chunk_without_revisions)

    # 3. For each lost object log a "deleted" revision with content identical
    # to the last logged revision.
    _recover_delete_revisions(
        # Every revision present in obj_rev_map has no object in the DB
        revisions_table,
        event,
        list(obj_rev_map.values()))

    db.session.commit()


def _update_existing_revisions(objects, revisions_table, obj_rev_map):
    """Update existing revisions with the result of log_json and remove
     the obj.id from obj_rev_map.
  """
    for obj in objects:
        rev_id = obj_rev_map.pop(obj.id)
        # Update revisions_table.content to the latest object's json
        db.session.execute(revisions_table.update()
                           .where(revisions_table.c.id == rev_id)
                           .values(content=obj.log_json()))


def _recover_delete_revisions(revisions_table, event,
                              last_available_revision_ids):
    """Log an action="deleted" copy for revisions with ids in passed list."""
    if not last_available_revision_ids:
        return
    columns_to_clone = sorted(
        set(c.name for c in revisions_table.c) -
        {"id", "event_id", "action", "created_at", "updated_at"})
    db.session.execute(revisions_table.insert().from_select(
        ["event_id", "action", "created_at", "updated_at"] + columns_to_clone,
        select(
            [event.id, literal("deleted"),
             func.now(), func.now()] + columns_to_clone, ).select_from(
                 revisions_table, ).where(
                     revisions_table.c.id.in_(last_available_revision_ids), ),
    ), )


def _recover_create_revisions(revisions_table, event, object_type,
                              chunk_without_revisions):
    """Log a "created"/"modified" revision for every passed object's json.

  If json["updated_at"] == json["created_at"], log action="created".
  If json["updated_at"] != json["created_at"], log action="modified".
  """

    def determine_action(obj_content):
        if obj_content.get("created_at") != obj_content.get("updated_at"):
            return "modified"
        else:
            return "created"

    # Every object with id not present in obj_
    object_ids_with_jsons = [(obj.id, obj.log_json())
                             for obj in chunk_without_revisions]

    if not object_ids_with_jsons:
        return

    db.session.execute(
        revisions_table.insert(),
        [{
            "resource_id":
            obj_id,
            "resource_type":
            object_type,
            "resource_slug":
            obj_content.get("slug"),
            "event_id":
            event.id,
            "action":
            determine_action(obj_content),
            "content":
            obj_content,
            "context_id":
            obj_content.get("context_id"),
            "modified_by_id":
            (obj_content.get("modified_by_id") or get_current_user_id()),
            "source_type":
            obj_content.get("source_type"),
            "source_id":
            obj_content.get("source_id"),
            "destination_type":
            obj_content.get("destination_type"),
            "destination_id":
            obj_content.get("destination_id")
        } for (obj_id, obj_content) in object_ids_with_jsons],
    )


def set_resource_slugs():
    with benchmark("set revision resource_slug content"):
        revisions_table = all_models.Revision.__table__
        rows = db.session.execute(
            select([
                revisions_table.c.id,
                revisions_table.c.content,
            ]).where(revisions_table.c.resource_type.in_(Types.all)).where(
                revisions_table.c.resource_slug.is_(None)))
        for row in rows:
            if row.content.get("slug"):
                db.session.execute(
                    revisions_table.update()
                    .where(revisions_table.c.id == row.id)
                    .values(resource_slug=row.content.get("slug")))
        db.session.commit()


def do_refresh_revisions():
    """Update last revisions of models with fixed data."""
    set_resource_slugs()
    event = all_models.Event(action="BULK")
    db.session.add(event)
    db.session.flush([event])

    # TODO: Improve performance/memory consumption so that we can run
    # _fix_type_revisions for all objects and not just the objects that are
    # snapshottable
    for type_ in sorted(Types.all | {"Assessment"}):
        logger.info("Updating revisions for: %s", type_)
        _fix_type_revisions(event, type_, get_revisions_by_type(type_))
