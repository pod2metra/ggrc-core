# Copyright (C) 2016 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
Migrate audits for snapshots

Create Date: 2016-11-17 11:49:04.547216
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from logging import getLogger

from alembic import op

from sqlalchemy.sql import and_
from sqlalchemy.sql import column
from sqlalchemy.sql import func
from sqlalchemy.sql import select
from sqlalchemy.sql import table

from ggrc.models.event import Event
from ggrc.models.relationship import Relationship
from ggrc.models.revision import Revision
from ggrc.models.snapshot import Snapshot

from ggrc.migrations.utils import create_snapshots
from ggrc.migrations.utils import create_relationships
from ggrc.migrations.utils import remove_relationships
from ggrc.migrations.utils import get_migration_user_id
from ggrc.migrations.utils import get_relationships
from ggrc.migrations.utils import get_relationship_cache
from ggrc.migrations.utils import get_revisions
from ggrc.migrations.utils import insert_payloads
from ggrc.migrations.utils import Stub

from ggrc.snapshotter.rules import Types


logger = getLogger(__name__)  # pylint: disable=invalid-name


# revision identifiers, used by Alembic.
revision = '142272c4a0b6'
down_revision = '1aa39778da75'

relationships_table = Relationship.__table__
events_table = Event.__table__
snapshots_table = Snapshot.__table__
revisions_table = Revision.__table__

audits_table = table(
    "audits",
    column("id"),
    column("context_id"),
    column("program_id"),
)

programs_table = table(
    "programs",
    column("id"),
    column("context_id")
)


def add_objects_to_program_scope(connection, event, user_id,
                                 program_id, program_context_id, objects):
  relationship_pairs = set()

  for obj in objects:
    relationship_pairs.add(("Program", program_id, obj[0], obj[1]))

  create_relationships(connection, event, program_context_id, user_id,
                       relationship_pairs)


def process_audits(connection, event, user_id, caches, audits):
  relationships_payload = []
  snapshots_payload = []

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
              "source_type": "Program",
              "source_id": audit.program_id,
              "destination_type": obj_.type,
              "destination_id": obj_.id,
              "modified_by_id": user_id,
              "context_id": program_contexts[audit.program_id],
          }]

    if audit_scope_objects:
      for obj_ in audit_scope_objects:
        if obj_ in revisions_cache:
          snapshots_payload += [{
            "parent_type": "Audit",
            "parent_id": audit.id,
            "child_type": obj_.type,
            "child_id": obj_.id,
            "revision_id": revisions_cache[obj_],
            "context_id": audit.context_id,
            "modified_by_id": user_id,
          }]

  insert_payloads(connection, event, user_id,
                  snapshots_payload, relationships_payload)


def validate_database(connection):
  audits_more = []
  ghost_objects = []

  tables = [
      "Assessment",
      "Issue",
  ]

  for klass_name in tables:
    sql_base_left = select([
        func.count(relationships_table.c.id).label("relcount"),
        relationships_table.c.source_id.label("object_id"),
    ]).where(
        and_(
            relationships_table.c.source_type == klass_name,
            relationships_table.c.destination_type == "Audit"
        )
    ).group_by(relationships_table.c.source_id)

    sql_base_right = select([
        func.count(relationships_table.c.id).label("relcount"),
        relationships_table.c.destination_id.label("object_id"),
    ]).where(
        and_(
            relationships_table.c.destination_type == klass_name,
            relationships_table.c.source_type == "Audit"
        )
    ).group_by(relationships_table.c.destination_id)

    sql_left_more = sql_base_left.having(sql_base_left.c.relcount > 1)
    sql_right_more = sql_base_right.having(sql_base_right.c.relcount > 1)
    sql_left_none = sql_base_left.having(sql_base_left.c.relcount == 0)
    sql_right_none = sql_base_right.having(sql_base_right.c.relcount == 0)

    result_left_more = connection.execute(sql_left_more).fetchall()
    result_right_more = connection.execute(sql_right_more).fetchall()
    result_more = result_left_more + result_right_more

    result_left_none = connection.execute(sql_left_none).fetchall()
    result_right_none = connection.execute(sql_right_none).fetchall()
    result_none = result_left_none + result_right_none

    if result_more:
      audits_more += [(klass_name, result_more)]
    if result_none:
      ghost_objects += [(klass_name, result_none)]
  return audits_more, ghost_objects


def upgrade():
  """Migrate audit-related data and concepts to audit snapshots"""
  connection = op.get_bind()

  audits_more, ghost_objects = validate_database(connection)

  corrupted_audit_ids = set()

  if audits_more or ghost_objects:
    for klass_name, result in audits_more:
      ids = [id_ for _, id_ in result]
      corrupted_audit_ids = corrupted_audit_ids.union(set(ids))
      print "The following {klass} have more than one Audit: {ids}".format(
          klass=klass_name,
          ids=",".join(map(str, ids))
      )
    for klass_name, result in ghost_objects:
      ids = [id_ for _, id_ in result]
      corrupted_audit_ids = corrupted_audit_ids.union(set(ids))
      print "The following {klass} have no Audits mapped to them: {ids}".format(
        klass=klass_name,
        ids=",".join(map(str, ids))
      )

    # TODO decide if we want to block migration before bigger mess is created
    # accidentally
    # raise Exception("Cannot perform migration.")

  audits = connection.execute(audits_table.select()).fetchall()
  if audits:
    program_ids = {audit.program_id for audit in audits}

    program_sql = select([programs_table]).where(
        programs_table.c.id.in_(program_ids)
    )
    programs = connection.execute(program_sql)
    program_contexts = {program.id: program.context_id for program in programs}

    program_relationships = get_relationship_cache(
        connection, "Program", Types.all)
    audit_relationships = get_relationship_cache(connection, "Audit", Types.all)

    audits = [audit for audit in audits if audit.id not in corrupted_audit_ids]

    all_objects = (program_relationships.values() + audit_relationships.values())
    revisionable_objects = set()
    revisionable_objects = revisionable_objects.union(*all_objects)
    revision_cache = get_revisions(connection, revisionable_objects)

    # TODO leave exception? remove?
    # objects_missing_revision = revisionable_objects - set(revision_cache.keys())
    # if objects_missing_revision:
    #   print objects_missing_revision
    #   raise Exception("There are still objects with missing revisions!")

    caches = {
        "program_contexts": program_contexts,
        "program_rels": program_relationships,
        "audit_rels": audit_relationships,
        "revisions": revision_cache
    }

    # TODO add MIGRATOR support
    user_id = get_migration_user_id(connection)

    event = {
      "action": "BULK",
      "resource_id": 0,
      "resource_type": 0,
      "context_id": 0,
      "modified_by_id": user_id
    }
    connection.execute(events_table.insert(), event)

    event_sql = select([events_table]).where(
      events_table.c.action == "BULK").order_by(
      events_table.c.id.desc()).limit(1)
    event = connection.execute(event_sql).fetchone()

    process_audits(connection, event, user_id, caches, audits)

def downgrade():
  pass
