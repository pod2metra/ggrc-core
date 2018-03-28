# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Place all public programs into their own context.

Create Date: 2013-12-06 00:20:15.108809
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa
from alembic import op
from datetime import datetime
from sqlalchemy.sql import table, column, select, and_

# revision identifiers, used by Alembic.
revision = 'c460b4f8cc3'
down_revision = '40a621571ac7'

contexts_table = table(
    'contexts',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('description', sa.Text),
    column('related_object_id', sa.Integer),
    column('related_object_type', sa.String),
    column('modified_by_id', sa.Integer),
    column('created_at', sa.DateTime),
    column('updated_at', sa.DateTime),
)

roles_table = table(
    'roles',
    column('id', sa.Integer),
    column('name', sa.String),
)

role_implications_table = table(
    'role_implications',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('source_context_id', sa.Integer),
    column('source_role_id', sa.Integer),
    column('role_id', sa.Integer),
    column('modified_by_id', sa.Integer),
    column('created_at', sa.DateTime),
    column('updated_at', sa.DateTime),
)

programs_table = table(
    'programs',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
)

object_documents_table = table(
    'object_documents',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('documentable_id', sa.Integer),
    column('documentable_type', sa.String),
)

object_people_table = table(
    'object_people',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('personable_id', sa.Integer),
    column('personable_type', sa.String),
)

object_objectives_table = table(
    'object_objectives',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('objectiveable_id', sa.Integer),
    column('objectiveable_type', sa.String),
)

relationships_table = table(
    'relationships',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('source_id', sa.Integer),
    column('source_type', sa.String),
    column('destination_id', sa.Integer),
    column('destination_type', sa.String),
)

program_controls_table = table(
    'program_controls',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('program_id', sa.Integer),
    column('control_id', sa.String),
)

program_directives_table = table(
    'program_directives',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('program_id', sa.Integer),
    column('directive_id', sa.String),
)

object_owners_table = table(
    'object_owners',
    column('id', sa.Integer),
    column('person_id', sa.Integer),
    column('ownable_id', sa.Integer),
    column('ownable_type', sa.String),
    column('modified_by_id', sa.Integer),
    column('created_at', sa.DateTime),
    column('updated_at', sa.DateTime),
)

user_roles_table = table(
    'user_roles',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('role_id', sa.Integer),
    column('person_id', sa.Integer),
    column('modified_by_id', sa.Integer),
    column('created_at', sa.DateTime),
    column('updated_at', sa.DateTime),
)


def get_role(name):
    connection = op.get_bind()
    return connection.execute(
        select(
            [roles_table.c.id]).where(roles_table.c.name == name)).fetchone()


def add_role_implication(context_id, source_context_id, source_role_id,
                         role_id):
    current_datetime = datetime.now()
    connection = op.get_bind()
    connection.execute(role_implications_table.insert().values(
        context_id=context_id,
        source_context_id=source_context_id,
        source_role_id=source_role_id,
        role_id=role_id,
        modified_by_id=1,
        created_at=current_datetime,
        updated_at=current_datetime,
    ))


def upgrade():
    reader_role = get_role('Reader')
    object_editor_role = get_role('ObjectEditor')
    program_creator_role = get_role('ProgramCreator')
    program_reader_role = get_role('ProgramReader')
    program_owner_role = get_role('ProgramOwner')

    connection = op.get_bind()
    programs = connection.execute(
        select([programs_table.c.id])
        .where(programs_table.c.context_id == None))  # noqa
    current_datetime = datetime.now()
    for program in programs:
        # Create the program context
        connection.execute(contexts_table.insert().values(
            context_id=1,
            description='',
            related_object_id=program.id,
            related_object_type='Program',
            modified_by_id=1,
            created_at=current_datetime,
            updated_at=current_datetime,
        ))
        context = connection.execute(
            select([contexts_table.c.id]).where(
                and_(contexts_table.c.related_object_id == program.id,
                     contexts_table.c.related_object_type ==
                     'Program'))).fetchone()
        context_id = context.id

        # Add the role implications that makes the program public
        for role in [reader_role, object_editor_role, program_creator_role]:
            add_role_implication(context_id, None, role.id,
                                 program_reader_role.id)

        # Move the program into the program context
        op.execute(programs_table.update().values(context_id=context_id)
                   .where(programs_table.c.id == program.id))

        # Add role assignments for owners and delete the object_owner relationships
        owners = connection.execute(
            select([object_owners_table.c.id, object_owners_table.c.person_id])
            .where(
                and_(object_owners_table.c.ownable_id == program.id,
                     object_owners_table.c.ownable_type ==
                     'Program'))).fetchall()
        for owner in owners:
            connection.execute(user_roles_table.insert().values(
                context_id=context_id,
                role_id=program_owner_role.id,
                person_id=owner.person_id,
                modified_by_id=1,
                created_at=current_datetime,
                updated_at=current_datetime,
            ))
            connection.execute(object_owners_table.delete().where(
                object_owners_table.c.id == owner.id))

        # Move all relationships for the program into the program context
        op.execute(object_documents_table.update().values(
            context_id=context_id).where(
                and_(object_documents_table.c.documentable_id == program.id,
                     object_documents_table.c.documentable_type == 'Program')))

        op.execute(
            object_people_table.update().values(context_id=context_id).where(
                and_(object_people_table.c.personable_id == program.id,
                     object_people_table.c.personable_type == 'Program')))

        op.execute(object_objectives_table.update(
        ).values(context_id=context_id).where(
            and_(object_objectives_table.c.objectiveable_id == program.id,
                 object_objectives_table.c.objectiveable_type == 'Program')))

        op.execute(
            relationships_table.update().values(context_id=context_id).where(
                and_(relationships_table.c.source_id == program.id,
                     relationships_table.c.source_type == 'Program')))

        op.execute(
            relationships_table.update().values(context_id=context_id).where(
                and_(relationships_table.c.destination_id == program.id,
                     relationships_table.c.destination_type == 'Program')))

        op.execute(
            program_controls_table.update().values(context_id=context_id)
            .where(program_controls_table.c.program_id == program.id))

        op.execute(
            program_directives_table.update().values(context_id=context_id)
            .where(program_directives_table.c.program_id == program.id))


def downgrade():
    reader_role = get_role('Reader')
    program_owner_role = get_role('ProgramOwner')
    connection = op.get_bind()
    # Find public programs by finding a public role implication
    reader_implications = connection.execute(
        select([role_implications_table.c.context_id])
        .where(role_implications_table.c.source_role_id == reader_role.id))
    current_datetime = datetime.now()
    for public_implication in reader_implications:
        context_id = public_implication.context_id

        # Move all relationships back to the NULL context
        op.execute(object_documents_table.update().values(context_id=None)
                   .where(object_documents_table.c.context_id == context_id))

        op.execute(object_people_table.update().values(context_id=None)
                   .where(object_people_table.c.context_id == context_id))

        op.execute(object_objectives_table.update().values(context_id=None)
                   .where(object_objectives_table.c.context_id == context_id))

        op.execute(relationships_table.update().values(context_id=None)
                   .where(relationships_table.c.context_id == context_id))

        op.execute(program_controls_table.update().values(context_id=None)
                   .where(program_controls_table.c.context_id == context_id))

        op.execute(program_directives_table.update().values(context_id=None)
                   .where(program_directives_table.c.context_id == context_id))

        # Remove the role implications that made the program public
        op.execute(role_implications_table.delete().where(
            role_implications_table.c.context_id == context_id))

        # Create ObjectOwner rows for each ProgramOwner role assignment, delete
        # the now defunct ProgramOwner assignments
        program = connection.execute(
            select([programs_table.c.id])
            .where(programs_table.c.context_id == context_id)).fetchone()
        program_owners = connection.execute(
            select(
                [user_roles_table.c.id, user_roles_table.c.person_id]).where(
                    and_(user_roles_table.c.context_id == context_id,
                         user_roles_table.c.role_id == program_owner_role.id)))
        for program_owner in program_owners:
            connection.execute(object_owners_table.insert().values(
                person_id=program_owner.person_id,
                ownable_id=program.id,
                ownable_type='Program',
                modified_by_id=1,
                created_at=current_datetime,
                updated_at=current_datetime,
            ))

        # Delete defunct role assignments
        connection.execute(user_roles_table.delete().where(
            user_roles_table.c.context_id == context_id))

        # Move the program back into the NULL context
        op.execute(programs_table.update().values(context_id=None)
                   .where(programs_table.c.context_id == context_id))

        # Remove the defunct context
        op.execute(
            contexts_table.delete().where(contexts_table.c.id == context_id))
