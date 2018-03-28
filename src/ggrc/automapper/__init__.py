# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Automapper generator."""

from datetime import datetime
from logging import getLogger

import sqlalchemy as sa
from sqlalchemy.orm import load_only
from sqlalchemy.sql.expression import literal_column

from ggrc import db
from ggrc.automapper import rules
from ggrc import login
from ggrc.models import all_models
from ggrc.models.audit import Audit
from ggrc.models.automapping import Automapping
from ggrc.models.relationship import Relationship, RelationshipsCache, Stub
from ggrc.models.issue import Issue
from ggrc.models import exceptions
from ggrc.rbac.permissions import is_allowed_update
from ggrc.models.cache import Cache
from ggrc.utils import benchmark

# pylint: disable=invalid-name
logger = getLogger(__name__)


class AutomapperGenerator(object):
    """Generator for automappings.

  Consumes automapping rules and newly created Relationships, creates
  autogenerated Relationships registering them in Automappings table.

  Note: we can rely on the order of src/dst pairs of queued and
  inserted mappings since we only queue ordered pairs (see `order`).
  """

    COUNT_LIMIT = 10000

    def __init__(self):
        self.processed = set()
        self.queue = set()
        self.auto_mappings = set()
        self.automapping_ids = set()
        self.related_cache = RelationshipsCache()

    def related(self, obj):
        """Return obj's relationship stubs"""
        if obj in self.related_cache.cache:
            return self.related_cache.cache[obj]

        # Pre-fetch neighborhood for enqueued objects since we're gonna need these
        # results in a few steps. This drastically reduces number of queries.
        stubs = {s for rel in self.queue for s in rel}
        stubs.add(obj)
        self.related_cache.populate_cache(stubs)

        return self.related_cache.cache[obj]

    @staticmethod
    def order(src, dst):
        return (src, dst) if src < dst else (dst, src)

    def generate_automappings(self, relationship):
        # pylint: disable=protected-access
        self.auto_mappings = set()
        with benchmark("Automapping generate_automappings"):
            # initial relationship is special since it is already created and
            # processing it would abort the loop so we manually enqueue the
            # neighborhood
            src = Stub.from_source(relationship)
            dst = Stub.from_destination(relationship)
            self._step(src, dst)
            self._step(dst, src)
            while self.queue:
                if len(self.auto_mappings) > self.COUNT_LIMIT:
                    break
                src, dst = entry = self.queue.pop()

                if {src.type, dst.type} != {"Audit", "Issue"}:
                    # Auditor doesn't have edit (+map) permission on the Audit,
                    # but the Auditor should be allowed to Raise an Issue.
                    # Since Issue-Assessment-Audit is the only rule that
                    # triggers Issue to Audit mapping, we should skip the
                    # permission check for it
                    if not (self._can_map_to(src, relationship)
                            and self._can_map_to(dst, relationship)):
                        continue

                created = self._ensure_relationship(src, dst)
                self.processed.add(entry)
                if not created:
                    # If the edge already exists it means that auto mappings for it have
                    # already been processed and it is safe to cut here.
                    continue
                self._step(src, dst)
                self._step(dst, src)

            if len(self.auto_mappings) <= self.COUNT_LIMIT:
                self._flush(relationship)
            else:
                relationship._json_extras = {  # pylint: disable=protected-access
                    'automapping_limit_exceeded': True
                }

    @staticmethod
    def _can_map_to(obj, parent_relationship):
        """True if the current user can edit obj in parent_relationship.context."""
        context_id = None
        if parent_relationship.context:
            context_id = parent_relationship.context.id
        elif parent_relationship.context_id:
            logger.warning("context is unset but context_id is set on a "
                           "relationship %r: context=%r, context_id=%r",
                           parent_relationship, parent_relationship.context,
                           parent_relationship.context_id)
            context_id = parent_relationship.context_id
        return is_allowed_update(obj.type, obj.id, context_id)

    def _flush(self, parent_relationship):
        """Manually INSERT generated automappings."""
        if not self.auto_mappings:
            return
        with benchmark("Automapping flush"):
            current_user_id = login.get_current_user_id()
            automapping_result = db.session.execute(
                Automapping.__table__.insert().values(
                    relationship_id=parent_relationship.id,
                    source_id=parent_relationship.source_id,
                    source_type=parent_relationship.source_type,
                    destination_id=parent_relationship.destination_id,
                    destination_type=parent_relationship.destination_type,
                ))
            automapping_id = automapping_result.inserted_primary_key[0]
            self.automapping_ids.add(automapping_id)
            now = datetime.now()
            # We are doing an INSERT IGNORE INTO here to mitigate a race condition
            # that happens when multiple simultaneous requests create the same
            # automapping. If a relationship object fails our unique constraint
            # it means that the mapping was already created by another request
            # and we can safely ignore it.
            inserter = Relationship.__table__.insert().prefix_with("IGNORE")
            original = self.order(
                Stub.from_source(parent_relationship),
                Stub.from_destination(parent_relationship))
            db.session.execute(
                inserter.values(
                    [{
                        "id": None,
                        "modified_by_id": current_user_id,
                        "created_at": now,
                        "updated_at": now,
                        "source_id": src.id,
                        "source_type": src.type,
                        "destination_id": dst.id,
                        "destination_type": dst.type,
                        "context_id": None,
                        "status": None,
                        "parent_id": parent_relationship.id,
                        "automapping_id": automapping_id,
                        "is_external": False
                    } for src, dst in self.auto_mappings
                     if (src, dst) != original]))  # (src, dst) is sorted

            self._set_audit_id_for_issues(automapping_id)

            cache = Cache.get_cache(create=True)
            if cache:
                # Add inserted relationships into new objects collection of the cache,
                # so that they will be logged within event and appropriate revisions
                # will be created.
                cache.new.update(
                    (relationship, relationship.log_json())
                    for relationship in Relationship.query.filter_by(
                        automapping_id=automapping_id, ))

    def propagate_acl(self):
        """Propagate acl records for newly created automappings"""

        if not self.automapping_ids:
            return

        rel = Relationship.__table__
        acl = all_models.AccessControlList.__table__
        acr = all_models.AccessControlRole.__table__
        propagate_roles = {
            "Program Managers": "Program Managers Mapped",
            "Program Editors": "Program Editors Mapped",
            "Program Readers": "Program Readers Mapped"
        }
        roles = all_models.AccessControlRole.query.filter(
            all_models.AccessControlRole.name.in_(
                propagate_roles.values() + list(propagate_roles))).options(
                    load_only("id", "name")).all()
        role_map = {role.name: role.id for role in roles}
        source = {"id": rel.c.source_id, "type": rel.c.source_type}
        destination = {
            "id": rel.c.destination_id,
            "type": rel.c.destination_type
        }

        for role in propagate_roles:
            prop_role_id = role_map[propagate_roles[role]]
            for (first, second) in ((source, destination), (destination,
                                                            source)):
                sql = sa.sql.expression.select([
                    acl.c.person_id,
                    literal_column(str(prop_role_id)), first["id"],
                    first["type"], acl.c.created_at, acl.c.updated_at, acl.c.id
                ]).select_from(
                    rel.join(acl,
                             sa.and_(
                                 second["id"] == acl.c.object_id,
                                 second["type"] == acl.c.object_type,
                             )).join(acr, acl.c.ac_role_id == acr.c.id)).where(
                                 sa.and_(
                                     rel.c.automapping_id.in_(
                                         self.automapping_ids),
                                     acr.c.name == role))
                db.session.execute(acl.insert().from_select([
                    acl.c.person_id, acl.c.ac_role_id, acl.c.object_id,
                    acl.c.object_type, acl.c.created_at, acl.c.updated_at,
                    acl.c.parent_id
                ], sql))

    @staticmethod
    def _set_audit_id_for_issues(automapping_id):
        """Set audit_id and context_id in automapped Issues."""
        iss, rel, aud = Issue.__table__, Relationship.__table__, Audit.__table__
        db.session.execute(
            sa.sql.expression.update(iss).values({
                iss.c.audit_id:
                aud.c.id,
                iss.c.context_id:
                aud.c.context_id,
            }).where(
                sa.and_(
                    rel.c.automapping_id == automapping_id,
                    rel.c.source_type == Audit.__name__,
                    rel.c.source_id == aud.c.id,
                    rel.c.destination_type == Issue.__name__,
                    rel.c.destination_id == iss.c.id,
                ), ))

    def _step(self, src, dst):
        mappings = rules.rules[src.type, dst.type]
        if mappings:
            dst_related = (o for o in self.related(dst)
                           if o.type in mappings and o != src)
            for r in dst_related:
                entry = self.order(r, src)
                if entry not in self.processed:
                    self.queue.add(entry)

    def _ensure_relationship(self, src, dst):
        """Create the relationship if not exists already.

    Returns:
      True if a relationship was created;
      False otherwise.
    """
        # even though self.cache is defaultdict, self.cache[key] adds key
        # to self.cache if it is not present, and we should avoid it
        if dst in self.related(src):
            return False
        if src in self.related(dst):
            return False

        self._check_single_audit_restriction(src, dst)

        self.auto_mappings.add((src, dst))

        if src in self.related_cache.cache:
            self.related_cache.cache[src].add(dst)
        if dst in self.related_cache.cache:
            self.related_cache.cache[dst].add(src)

        return True

    def _check_single_audit_restriction(self, src, dst):
        """Fail if dst (Issue) is already mapped to an Audit."""
        # src, dst are ordered since they come from self.queue
        if (src.type, dst.type) == ("Audit", "Issue"):
            if "Audit" in (r.type for r in self.related(dst)):
                raise exceptions.ValidationError(
                    "This request will result in automapping that will map "
                    "Issue#{issue.id} to multiple Audits.".format(issue=dst))


def register_automapping_listeners():
    """Register event listeners for auto mapper."""

    # pylint: disable=unused-variable,unused-argument

    def automap(session, _):
        """Automap after_flush handler."""
        automapper = AutomapperGenerator()
        for obj in session.new:
            if isinstance(obj, Relationship):
                automapper.generate_automappings(obj)
        automapper.propagate_acl()

    sa.event.listen(sa.orm.session.Session, "after_flush", automap)
