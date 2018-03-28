# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Move existing Workflows to new contexts

Create Date: 2014-07-22 20:34:07.052212
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op
import sqlalchemy as sa
from datetime import datetime
from sqlalchemy.sql import table, column, select, and_

# revision identifiers, used by Alembic.
revision = '4b3316aa1acf'
down_revision = '292222c25829'

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

context_implications_table = table(
    'context_implications',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('source_context_id', sa.Integer),
    column('context_scope', sa.String),
    column('source_context_scope', sa.String),
    column('modified_by_id', sa.Integer),
    column('created_at', sa.DateTime),
    column('updated_at', sa.DateTime),
)

workflows_table = table(
    'workflows',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
)

workflow_objects_table = table(
    'workflow_objects',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('workflow_id', sa.Integer),
)

workflow_people_table = table(
    'workflow_people',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('workflow_id', sa.Integer),
    column('person_id', sa.Integer),
)

workflow_tasks_table = table(
    'workflow_tasks',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('workflow_id', sa.Integer),
)

task_groups_table = table(
    'task_groups',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('workflow_id', sa.Integer),
)

task_group_objects_table = table(
    'task_group_objects',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('task_group_id', sa.Integer),
)

task_group_tasks_table = table(
    'task_group_tasks',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('task_group_id', sa.Integer),
)

cycles_table = table(
    'cycles',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('workflow_id', sa.Integer),
)

cycle_task_groups_table = table(
    'cycle_task_groups',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('cycle_id', sa.Integer),
)

cycle_task_entries_table = table(
    'cycle_task_entries',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('cycle_id', sa.Integer),
)

cycle_task_group_objects_table = table(
    'cycle_task_group_objects',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('cycle_id', sa.Integer),
)

cycle_task_group_object_tasks_table = table(
    'cycle_task_group_object_tasks',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('cycle_id', sa.Integer),
)

object_files_table = table(
    'object_files',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('fileable_id', sa.Integer),
    column('fileable_type', sa.String),
)

object_folders_table = table(
    'object_folders',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('folderable_id', sa.Integer),
    column('folderable_type', sa.String),
)

object_owners_table = table(
    'object_owners',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('person_id', sa.Integer),
    column('ownable_id', sa.Integer),
    column('ownable_type', sa.String),
)


def get_role(name):
    connection = op.get_bind()
    return connection.execute(
        select(
            [roles_table.c.id]).where(roles_table.c.name == name)).fetchone()


def upgrade():
    current_datetime = datetime.now()

    # Get the roles we'll need later
    workflow_owner_role = get_role('WorkflowOwner')
    workflow_member_role = get_role('WorkflowMember')

    # Get all current workflows
    connection = op.get_bind()
    workflows = connection.execute(
        select([workflows_table.c.id])
        .where(workflows_table.c.context_id == None))  # noqa

    for workflow in workflows:
        workflow_id = workflow.id

        # Create the Workflow context
        connection.execute(contexts_table.insert().values(
            context_id=None,
            description='',
            related_object_id=workflow_id,
            related_object_type='Workflow',
            modified_by_id=1,
            created_at=current_datetime,
            updated_at=current_datetime,
        ))

        # Get the context id
        context = connection.execute(
            select([contexts_table.c.id]).where(
                and_(contexts_table.c.related_object_id == workflow_id,
                     contexts_table.c.related_object_type ==
                     'Workflow'))).fetchone()
        context_id = context.id

        # Move the Workflow into the new context
        op.execute(workflows_table.update().values(context_id=context_id)
                   .where(workflows_table.c.id == workflow_id))

    # Now, select *all* workflows, since the rest applies to all equally
    workflows = connection.execute(
        select([workflows_table.c.id, workflows_table.c.context_id]))

    for workflow in workflows:
        workflow_id = workflow.id
        context_id = workflow.context_id

        # Create the Context Implications to/from the Workflow context
        op.execute(context_implications_table.insert().values(
            source_context_id=context_id,
            source_context_scope='Workflow',
            context_id=None,
            context_scope=None,
            modified_by_id=1,
            created_at=current_datetime,
            updated_at=current_datetime))

        op.execute(context_implications_table.insert().values(
            source_context_id=None,
            source_context_scope=None,
            context_id=context_id,
            context_scope='Workflow',
            modified_by_id=1,
            created_at=current_datetime,
            updated_at=current_datetime))

        # Add role assignments for owners and delete the object_owner relationships
        owners = connection.execute(
            select([object_owners_table.c.id, object_owners_table.c.person_id])
            .where(
                and_(object_owners_table.c.ownable_id == workflow_id,
                     object_owners_table.c.ownable_type ==
                     'Workflow'))).fetchall()

        for owner in owners:
            connection.execute(user_roles_table.insert().values(
                context_id=context_id,
                role_id=workflow_owner_role.id,
                person_id=owner.person_id,
                modified_by_id=1,
                created_at=current_datetime,
                updated_at=current_datetime,
            ))
            connection.execute(object_owners_table.delete().where(
                object_owners_table.c.id == owner.id))

        # Add role assignments for WorkflowPerson objects
        members = connection.execute(
            select([workflow_people_table.c.person_id
                    ]).where(workflow_people_table.c.workflow_id ==
                             workflow_id)).fetchall()

        for member in members:
            connection.execute(user_roles_table.insert().values(
                context_id=context_id,
                role_id=workflow_member_role.id,
                person_id=member.person_id,
                modified_by_id=1,
                created_at=current_datetime,
                updated_at=current_datetime,
            ))
        '''
    directly_connected_tables = [
        workflow_objects_table,
        workflow_people_table,
        workflow_tasks_table,
        task_groups_table,
        cycles_table,
        ]

    polymorphically_connected_tables = [
        object_files_table,
        object_folders_table,
        object_owners_table,
        ]

    cycle_connected_tables = [
        cycle_task_groups_table,
        cycle_task_entries_table,
        cycle_task_group_objects_table,
        cycle_task_group_object_tasks_table,
        ]
    '''

        # Update rows for directly-connected tables
        op.execute(
            workflow_objects_table.update().values(context_id=context_id)
            .where(workflow_objects_table.c.workflow_id == workflow_id))

        op.execute(
            workflow_people_table.update().values(context_id=context_id)
            .where(workflow_people_table.c.workflow_id == workflow_id))

        op.execute(workflow_tasks_table.update().values(context_id=context_id)
                   .where(workflow_tasks_table.c.workflow_id == workflow_id))

        op.execute(task_groups_table.update().values(context_id=context_id)
                   .where(task_groups_table.c.workflow_id == workflow_id))

        op.execute(
            task_group_objects_table.update().values(context_id=context_id)
            .where(
                task_group_objects_table.c.task_group_id.in_(
                    select([task_groups_table.c.id])
                    .where(task_groups_table.c.workflow_id == workflow_id))))

        op.execute(task_group_tasks_table.update().values(
            context_id=context_id).where(
                task_group_tasks_table.c.task_group_id.in_(
                    select([task_groups_table.c.id])
                    .where(task_groups_table.c.workflow_id == workflow_id))))

        op.execute(cycles_table.update().values(context_id=context_id)
                   .where(cycles_table.c.workflow_id == workflow_id))

        # Update rows for polymorphically-connected tables
        op.execute(
            object_files_table.update().values(context_id=context_id).where(
                and_(object_files_table.c.fileable_id == workflow_id,
                     object_files_table.c.fileable_type == 'Workflow')))

        op.execute(
            object_folders_table.update().values(context_id=context_id).where(
                and_(object_folders_table.c.folderable_id == workflow_id,
                     object_folders_table.c.folderable_type == 'Workflow')))

        # Update rows for cycle-connected tables
        op.execute(cycle_task_entries_table.update()
                   .values(context_id=context_id).where(
                       cycle_task_entries_table.c.cycle_id.in_(
                           select([cycles_table.c.id])
                           .where(cycles_table.c.workflow_id == workflow_id))))

        op.execute(cycle_task_groups_table.update()
                   .values(context_id=context_id).where(
                       cycle_task_groups_table.c.cycle_id.in_(
                           select([cycles_table.c.id])
                           .where(cycles_table.c.workflow_id == workflow_id))))

        op.execute(cycle_task_group_objects_table.update()
                   .values(context_id=context_id).where(
                       cycle_task_group_objects_table.c.cycle_id.in_(
                           select([cycles_table.c.id])
                           .where(cycles_table.c.workflow_id == workflow_id))))

        op.execute(cycle_task_group_object_tasks_table.update()
                   .values(context_id=context_id).where(
                       cycle_task_group_object_tasks_table.c.cycle_id.in_(
                           select([cycles_table.c.id])
                           .where(cycles_table.c.workflow_id == workflow_id))))


def downgrade():
    pass
