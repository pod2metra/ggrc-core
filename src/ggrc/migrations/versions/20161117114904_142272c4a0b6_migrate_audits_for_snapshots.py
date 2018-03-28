# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Migrate audits for snapshots

Create Date: 2016-11-17 11:49:04.547216
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from logging import getLogger

from alembic import op

from sqlalchemy.sql import column
from sqlalchemy.sql import select
from sqlalchemy.sql import table
from sqlalchemy.sql import tuple_

from ggrc.models.event import Event
from ggrc.models.revision import Revision
from ggrc.models.snapshot import Snapshot
from ggrc.models.assessment import Assessment
from ggrc.models.issue import Issue

from ggrc.migrations.utils import get_relationship_cache
from ggrc.migrations.utils import get_revisions
from ggrc.migrations.utils import insert_payloads
from ggrc.migrations.utils import Stub
from ggrc.migrations.utils.validation import (
    validate_assessment_issue_to_audit_relationships)

from ggrc.migrations.utils.migrator import get_migration_user_id

from ggrc.snapshotter.rules import Types

logger = getLogger(__name__)  # pylint: disable=invalid-name

# revision identifiers, used by Alembic.
revision = '142272c4a0b6'
down_revision = '579239d161e1'

events_table = Event.__table__
snapshots_table = Snapshot.__table__
revisions_table = Revision.__table__

assessments_table = Assessment.__table__
issues_table = Issue.__table__

audits_table = table(
    "audits",
    column("id"),
    column("context_id"),
    column("program_id"),
)

programs_table = table("programs", column("id"), column("context_id"))


def create_snapshots(connection, user_id, caches, audits):
    """Create snapshots and relationships to programs"""
    # pylint: disable=too-many-locals
    relationships_payload = []
    snapshots_payload = []
    snapshot_quads = set()

    program_relationships = caches["program_rels"]
    audit_relationships = caches["audit_rels"]
    program_contexts = caches["program_contexts"]
    revisions_cache = caches["revisions"]

    for audit in audits:
        parent_key = Stub("Audit", audit.id)
        program_key = Stub("Program", audit.program_id)
        audit_scope_objects = audit_relationships[parent_key]
        program_scope_objects = program_relationships[program_key]
        missing_in_program_scope = audit_scope_objects - program_scope_objects

        if missing_in_program_scope:
            for obj_ in missing_in_program_scope:
                if obj_ in revisions_cache:
                    relationships_payload += [{
                        "source_type":
                        "Program",
                        "source_id":
                        audit.program_id,
                        "destination_type":
                        obj_.type,
                        "destination_id":
                        obj_.id,
                        "modified_by_id":
                        user_id,
                        "context_id":
                        program_contexts[audit.program_id],
                    }]

        if audit_scope_objects:
            for obj_ in audit_scope_objects:
                if obj_ in revisions_cache:
                    quad = ("Audit", audit.id, obj_.type, obj_.id)
                    snapshot_quads.add(quad)
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
                        audit.context_id,
                        "modified_by_id":
                        user_id,
                    }]
                    # this is because of our hack where we rely on relationships
                    # to actually show objects
                    relationships_payload += [{
                        "source_type": "Audit",
                        "source_id": audit.id,
                        "destination_type": obj_.type,
                        "destination_id": obj_.id,
                        "modified_by_id": user_id,
                        "context_id": audit.context_id,
                    }]
                else:
                    logger.warning("Missing revision for object %s-%s",
                                   obj_.type, obj_.id)

    insert_payloads(connection, snapshots_payload, relationships_payload)
    return snapshot_quads


def process_audits(connection, user_id, caches, audits):
    """Process audits"""
    snapshot_quads = create_snapshots(connection, user_id, caches, audits)

    relationships_payload = []
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
                           obj_.child_id): (obj_.id, obj_.context_id)
                          for obj_ in snapshots}
        for snapshot in snapshot_quads:
            relationships_payload += [{
                "source_type":
                snapshot[2],
                "source_id":
                snapshot[3],
                "destination_type":
                "Snapshot",
                "destination_id":
                snapshot_cache[snapshot][0],
                "modified_by_id":
                user_id,
                "context_id":
                snapshot_cache[snapshot][1],
            }]

        insert_payloads(connection, relationships=relationships_payload)


def upgrade():
    """Migrate audit-related data and concepts to audit snapshots"""
    # pylint: disable=too-many-locals

    connection = op.get_bind()

    audits_more, ghost_objects = (
        validate_assessment_issue_to_audit_relationships(connection))

    if audits_more or ghost_objects:
        if audits_more:
            for klass_name, ids in audits_more.items():
                logger.warning(
                    "The following %s have more than one Audit: %s",
                    klass_name,
                    ",".join(map(str, ids))  # pylint: disable=bad-builtin
                )
        if ghost_objects:
            for klass_name, ids in ghost_objects.items():
                logger.warning(
                    "The following %s have no Audits mapped to them: %s",
                    klass_name,
                    ",".join(map(str, ids))  # pylint: disable=bad-builtin
                )
        raise Exception("Cannot perform migration. Check logger warnings.")

    audits = connection.execute(audits_table.select()).fetchall()
    if audits:
        program_ids = {audit.program_id for audit in audits}

        program_sql = select([programs_table]).where(
            programs_table.c.id.in_(program_ids))
        programs = connection.execute(program_sql)
        program_contexts = {
            program.id: program.context_id
            for program in programs
        }

        program_relationships = get_relationship_cache(connection, "Program",
                                                       Types.all)
        audit_relationships = get_relationship_cache(connection, "Audit",
                                                     Types.all)

        all_objects = (
            program_relationships.values() + audit_relationships.values())
        revisionable_objects = set()
        revisionable_objects = revisionable_objects.union(*all_objects)
        revision_cache = get_revisions(connection, revisionable_objects)

        objects_missing_revision = (
            revisionable_objects - set(revision_cache.keys()))
        if objects_missing_revision:
            missing = ",".join([
                "{obj.type}-{obj.id}".format(obj=obj)
                for obj in objects_missing_revision
            ])
            logger.warning("Phantom objects mapped to program or audit: %s",
                           missing)

        caches = {
            "program_contexts": program_contexts,
            "program_rels": program_relationships,
            "audit_rels": audit_relationships,
            "revisions": revision_cache
        }

        user_id = get_migration_user_id(connection)

        process_audits(connection, user_id, caches, audits)


def downgrade():
    pass
