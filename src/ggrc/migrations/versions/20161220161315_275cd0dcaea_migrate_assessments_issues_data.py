# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
migrate-assessments-issues-data

Create Date: 2016-12-20 16:13:15.208946
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from collections import defaultdict
from logging import getLogger

from alembic import op

from sqlalchemy.sql import column
from sqlalchemy.sql import select
from sqlalchemy.sql import table
from sqlalchemy.sql import tuple_

from ggrc.models.assessment import Assessment
from ggrc.models.event import Event
from ggrc.models.issue import Issue
from ggrc.models.revision import Revision
from ggrc.models.snapshot import Snapshot

from ggrc.snapshotter.rules import Types

from ggrc.migrations.utils import get_relationship_cache
from ggrc.migrations.utils import get_revisions
from ggrc.migrations.utils import insert_payloads
from ggrc.migrations.utils import Stub
from ggrc.migrations.utils.migrator import get_migration_user_id

logger = getLogger(__name__)  # pylint: disable=invalid-name

# revision identifiers, used by Alembic.
revision = '275cd0dcaea'
down_revision = '142272c4a0b6'

assessments_table = Assessment.__table__
issues_table = Issue.__table__
snapshots_table = Snapshot.__table__
revisions_table = Revision.__table__
events_table = Event.__table__

audits_table = table(
    "audits",
    column("id"),
    column("context_id"),
    column("program_id"),
)

programs_table = table("programs", column("id"), column("context_id"))


def process_objects(connection, user_id, caches, object_settings):
    """Process objects

  Used for processing of Assessments and Issues
  """
    # pylint: disable=too-many-locals

    snapshot_quads = get_or_create_snapshots(connection, user_id, caches,
                                             object_settings)

    link_snapshots_to_objects(connection, user_id, caches, object_settings,
                              snapshot_quads)


def get_or_create_snapshots(connection, user_id, caches, object_settings):
    """Get or create snapshots for specific object type"""
    # pylint: disable=too-many-locals
    relationships_payload = []
    snapshots_payload = []
    snapshot_quads = set()

    program_relationships = caches["program_rels"]
    parent_snapshot_cache = caches["snapshots"]
    program_contexts = caches["program_contexts"]
    audit_programs = caches["audit_programs"]
    audit_contexts = caches["audit_contexts"]
    revisions_cache = caches["revisions"]

    object_klass = object_settings["type"]
    object_relationships = object_settings["object_relationships"]
    object_select = object_settings["select_all"]

    all_objects = connection.execute(object_select).fetchall()

    for object_ in all_objects:
        key = Stub(object_klass, object_.id)
        objects = object_relationships[key]
        audit = [x for x in objects if x.type == "Audit"]
        others = [x for x in objects if x.type in Types.all]

        if len(audit) != 1:
            continue

        if audit:
            audit = audit[0]
            others = set(others)

            quads = {("Audit", audit.id, obj_.type, obj_.id)
                     for obj_ in others}
            snapshot_quads.update(quads)

            program_id = audit_programs[audit.id]
            program_ctx_id = program_contexts[program_id]

            existing_snapshots = parent_snapshot_cache[audit]
            missing_snapshots = others - existing_snapshots

            if missing_snapshots:
                audit_context_id = audit_contexts[audit.id]

                for obj_ in missing_snapshots:
                    if obj_ in revisions_cache:
                        snapshots_payload += [{
                            "parent_type":
                            "Audit",
                            "parent_id":
                            audit.id,
                            "child_type":
                            obj_.type,
                            "child_id":
                            obj_.id,
                            "revision_id":
                            revisions_cache[obj_],
                            "context_id":
                            audit_context_id,
                            "modified_by_id":
                            user_id,
                        }]
                        relationships_payload += [
                            {
                                "source_type": "Program",
                                "source_id": program_id,
                                "destination_type": obj_.type,
                                "destination_id": obj_.id,
                                "modified_by_id": user_id,
                                "context_id": program_ctx_id,
                            },
                            {
                                # this is because of our hack where we rely on
                                # relationships
                                "source_type": "Audit",
                                "source_id": audit.id,
                                "destination_type": obj_.type,
                                "destination_id": obj_.id,
                                "modified_by_id": user_id,
                                "context_id": audit_context_id,
                            }
                        ]
                    else:
                        logger.warning("Missing revision for object %s-%s",
                                       obj_.type, obj_.id)

                missing_from_program_scope = (
                    program_relationships[program_id] - existing_snapshots)
                if missing_from_program_scope:
                    for obj_ in missing_from_program_scope:
                        relationships_payload += [{
                            "source_type":
                            "Program",
                            "source_id":
                            program_id,
                            "destination_type":
                            obj_.type,
                            "destination_id":
                            obj_.id,
                            "modified_by_id":
                            user_id,
                            "context_id":
                            program_ctx_id,
                        }]

    insert_payloads(connection, snapshots_payload, relationships_payload)
    return snapshot_quads


def link_snapshots_to_objects(connection, user_id, caches, object_settings,
                              snapshot_quads):
    """Create relationships between snapshots and objects"""
    # pylint: disable=too-many-locals
    relationships_payload = []

    audit_contexts = caches["audit_contexts"]

    object_klass = object_settings["type"]
    object_relationships = object_settings["object_relationships"]
    object_select = object_settings["select_all"]

    all_objects = connection.execute(object_select).fetchall()

    if snapshot_quads:
        snapshots = connection.execute(
            select([snapshots_table]).where(
                tuple_(
                    Snapshot.parent_type,
                    Snapshot.parent_id,
                    Snapshot.child_type,
                    Snapshot.child_id,
                ).in_(snapshot_quads))).fetchall()
        snapshot_cache = {(obj_.parent_type, obj_.parent_id, obj_.child_type,
                           obj_.child_id): obj_.id
                          for obj_ in snapshots}

        for object_ in all_objects:
            key = Stub(object_klass, object_.id)
            objects = object_relationships[key]
            audit = [x for x in objects if x.type == "Audit"]
            others = [x for x in objects if x.type in Types.all]

            if len(audit) != 1:
                continue

            if audit:
                audit = audit[0]
                audit_context_id = audit_contexts[audit.id]
                others = set(others)

                for obj_ in others:
                    quad = ("Audit", audit.id, obj_.type, obj_.id)
                    if quad in snapshot_cache:
                        relationships_payload += [{
                            "source_type":
                            object_klass,
                            "source_id":
                            object_.id,
                            "destination_type":
                            "Snapshot",
                            "destination_id":
                            snapshot_cache[quad],
                            "modified_by_id":
                            user_id,
                            "context_id":
                            audit_context_id,
                        }, {
                            "source_type":
                            obj_.type,
                            "source_id":
                            obj_.id,
                            "destination_type":
                            "Snapshot",
                            "destination_id":
                            snapshot_cache[quad],
                            "modified_by_id":
                            user_id,
                            "context_id":
                            audit_context_id,
                        }]
                    else:
                        logger.warning(
                            "Couldn't map %s-%s to Snapshot of object %s-%s because it "
                            "doesn't exist due to missing revision.",
                            object_klass, object_.id, obj_.type, obj_.id)

    insert_payloads(connection, relationships=relationships_payload)


def get_scope_snapshots(connection):
    """Create cache of audit snapshots

  Create cache (defaultdict) of audits mapping from audit stub to set of
  children stubs.
  """
    cache = defaultdict(set)

    query = select([snapshots_table])
    result = connection.execute(query)
    for snapshot in result:
        parent = Stub(snapshot.parent_type, snapshot.parent_id)
        child = Stub(snapshot.child_type, snapshot.child_id)
        cache[parent].add(child)
    return cache


def upgrade():
    """Primary upgrade function for upgrading assessments and issues

  Primarily used for building various caches et al."""
    # pylint: disable=too-many-locals
    connection = op.get_bind()

    program_sql = select([programs_table])
    programs = connection.execute(program_sql)
    program_contexts = {program.id: program.context_id for program in programs}

    audit_sql = select([audits_table])
    audits = connection.execute(audit_sql).fetchall()
    if audits:
        audit_contexts = {audit.id: audit.context_id for audit in audits}
        audit_programs = {audit.id: audit.program_id for audit in audits}

        program_cache = get_relationship_cache(connection, "Program",
                                               Types.all)
        audit_cache = get_relationship_cache(connection, "Audit", Types.all)
        parent_snapshot_cache = get_scope_snapshots(connection)
        assessments_cache = get_relationship_cache(connection, "Assessment",
                                                   Types.all | {"Audit"})
        issues_cache = get_relationship_cache(connection, "Issue",
                                              Types.all | {"Audit"})

        all_objects = (program_cache.values() + audit_cache.values() +
                       assessments_cache.values() + issues_cache.values())

        revisionable_objects = set()
        revisionable_objects = revisionable_objects.union(*all_objects)
        revision_cache = get_revisions(connection, revisionable_objects)

        caches = {
            "program_rels": program_cache,
            "audit_rels": audit_cache,
            "snapshots": parent_snapshot_cache,
            "program_contexts": program_contexts,
            "audit_programs": audit_programs,
            "audit_contexts": audit_contexts,
            "revisions": revision_cache
        }

        objects = [
            {
                "type": "Assessment",
                "select_all": assessments_table.select(),
                "object_relationships": assessments_cache
            },
            {
                "type": "Issue",
                "select_all": issues_table.select(),
                "object_relationships": issues_cache
            },
        ]

        if assessments_cache or issues_cache:
            user_id = get_migration_user_id(connection)

            for object_settings in objects:
                process_objects(connection, user_id, caches, object_settings)


def downgrade():
    pass
