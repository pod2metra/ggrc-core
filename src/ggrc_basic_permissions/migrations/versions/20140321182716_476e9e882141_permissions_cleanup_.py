# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Permissions cleanup migrations

Revision ID: 476e9e882141
Revises: 387cf5a9a3ad
Create Date: 2014-03-21 18:27:16.802081

"""

# revision identifiers, used by Alembic.
revision = '476e9e882141'
down_revision = '387cf5a9a3ad'

from alembic import op
from datetime import datetime
from sqlalchemy.sql import table, column, select, insert, and_, or_
import sqlalchemy as sa

context_implications_table = table(
    'context_implications',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('source_context_id', sa.Integer),
    column('context_scope', sa.String),
    column('source_context_scope', sa.String),
    column('updated_at', sa.DateTime),
    column('modified_by_id', sa.Integer),
)

contexts_table = table(
    'contexts',
    column('id', sa.Integer),
    column('related_object_id', sa.Integer),
    column('related_object_type', sa.String),
)

roles_table = table(
    'roles',
    column('id', sa.Integer),
    column('name', sa.String),
    column('scope', sa.String),
    column('description', sa.Text),
)

user_roles_table = table(
    'user_roles',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('role_id', sa.Integer),
    column('person_id', sa.Integer),
)

programs_table = table(
    'programs',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
)

audits_table = table(
    'audits',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
)

people_table = table(
    'people',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
)


def upgrade():
    connection = op.get_bind()

    # Find contexts without matching related objects
    context_ids = connection.execute(select([contexts_table.c.id])).fetchall()
    context_ids = [x for (x, ) in context_ids]

    program_context_ids = connection.execute(
        select([programs_table.c.context_id])).fetchall()
    program_context_ids = [x for (x, ) in program_context_ids]

    audit_context_ids = connection.execute(
        select([audits_table.c.context_id])).fetchall()
    audit_context_ids = [x for (x, ) in audit_context_ids]

    people_context_ids = connection.execute(
        select([people_table.c.context_id])).fetchall()
    people_context_ids = [x for (x, ) in people_context_ids]

    # Common and Admin contexts
    legitimate_context_ids = [0, 1]
    # Other still-valid contexts
    legitimate_context_ids = legitimate_context_ids +\
        program_context_ids + audit_context_ids + people_context_ids

    orphan_context_ids = set(context_ids) - set(legitimate_context_ids)
    print "Orphaned Contexts:"
    print orphan_context_ids

    # Find UserRole and ContextImplication objects using orphaned contexts and
    #   remove them
    if len(orphan_context_ids) > 0:
        op.execute(user_roles_table.delete().where(
            user_roles_table.c.context_id.in_(orphan_context_ids)))

    if len(orphan_context_ids) > 0:
        op.execute(context_implications_table.delete().where(
            or_(
                context_implications_table.c.source_context_id.in_(
                    orphan_context_ids),
                context_implications_table.c.context_id.in_(
                    orphan_context_ids),
            )))

    # Remove the contexts themselves
    # (Actually, don't, since it may cause referential integrity errors, and we
    #  don't want to implicitly cascade to other objects.)
    #if len(orphan_context_ids) > 0:
    #  op.execute(
    #      contexts_table.delete().where(
    #        context_table.c.id.in_(orphan_context_ids)))

    # Remove `RoleReader` assignments
    role_reader_role_ids = connection.execute(
        select([roles_table.c.id])\
          .where(roles_table.c.name == "RoleReader")
        ).fetchall()
    role_reader_role_ids = [x for (x, ) in role_reader_role_ids]

    if len(role_reader_role_ids) > 0:
        op.execute(user_roles_table.delete().where(
            user_roles_table.c.role_id.in_(role_reader_role_ids)))

    # Remove `RoleReader` role itself
    if len(role_reader_role_ids) > 0:
        op.execute(roles_table.delete().where(
            roles_table.c.id.in_(role_reader_role_ids)))

    # Find all UserRole objects for the same `person_id` and `context_id`, and
    #   remove all but the "strongest"

    # First, get all Role objects with names
    role_ids_with_names = connection.execute(
        select([roles_table.c.id, roles_table.c.name,
                roles_table.c.scope])).fetchall()
    roles_by_id = {}
    for (id, name, scope) in role_ids_with_names:
        roles_by_id[id] = (name, scope)

    user_role_tuples = connection.execute(
        select([
            user_roles_table.c.id,
            user_roles_table.c.context_id,
            user_roles_table.c.person_id,
            user_roles_table.c.role_id,
        ])).fetchall()
    user_role_items = {}
    for (id, context_id, person_id, role_id) in user_role_tuples:
        user_role_items\
            .setdefault((context_id, person_id), [])\
            .append((id, context_id, role_id))

    role_strengths = {
        "Auditor": 1,
        "Reader": 1,
        "ObjectEditor": 2,
        "ProgramCreator": 3,
        "gGRC Admin": 4,
        "ProgramReader": 1,
        "ProgramEditor": 2,
        "ProgramOwner": 3
    }

    user_role_ids_to_delete = []
    for _, user_role_items in user_role_items.items():
        if len(user_role_items) > 1:
            print("{} UserRole assignments:".format(len(user_role_items)))
            ids_with_role_strengths = []
            for (id, context_id, role_id) in user_role_items:
                role_name, role_scope = roles_by_id.get(role_id, None)

                # One-off check for bad context/scope pairs
                if context_id in (None, 0, 1)\
                    and role_name not in (
                        "gGRC Admin", "Reader", "ObjectEditor", "ProgramCreator"):
                    print("Invalid system role: context_id={}, role_id={}".
                          format(context_id, role_id))
                elif context_id not in (None, 0, 1)\
                    and role_name not in (
                        "Auditor", "ProgramReader", "ProgramEditor", "ProgramOwner"):
                    print("Invalid non-system role: context_id={}, role_id={}".
                          format(context_id, role_id))
                else:
                    if role_name:
                        strength = role_strengths.get(role_name, None)
                        if strength:
                            ids_with_role_strengths.append((id, strength))
                            print("Found user_role.id={}, {}".format(
                                id, role_name))
                        else:
                            print(
                                "Found unknown role name: {}, user_role.id={}".
                                format(role_name, id))
                    else:
                        print("Found bad role_id: {}".format(role_id))
            # Get the `id` with the highest "strength"
            keep_id = max(ids_with_role_strengths, key=lambda x: x[1])[0]
            ids_to_delete = [
                id for (id, _) in ids_with_role_strengths if id != keep_id
            ]
            print("Keeping {}, deleting {}".format(keep_id, ids_to_delete))
            user_role_ids_to_delete.extend(ids_to_delete)

    if len(user_role_ids_to_delete) > 0:
        op.execute(user_roles_table.delete().where(
            user_roles_table.c.id.in_(user_role_ids_to_delete)))

    # Update ProgramEditor Role description
    new_description = """A user with authorization to edit mapping objects related to an access controlled program.<br/><br/>When a person has this role they can map and unmap objects to the Program and edit the Program info, but they are unable to delete the Program or assign other people roles for that program."""
    op.execute(
        roles_table.update()\
            .where(roles_table.c.name == "ProgramEditor")\
            .values({ 'description': new_description }))


def downgrade():
    # None of these are reversible (except ProgramEditor description, but don't
    #   want it reversed)
    pass
