# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add audit permissions.

Revision ID: 904377398db
Revises: 4838619603a
Create Date: 2013-10-28 17:30:26.084569

"""

import json
import sqlalchemy as sa
from alembic import op
from datetime import datetime
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = '904377398db'
down_revision = '4838619603a'

roles_table = table(
    'roles',
    column('id', sa.Integer),
    column('name', sa.String),
    column('permissions_json', sa.Text),
    column('description', sa.Text),
    column('modified_by_id', sa.Integer),
    column('created_at', sa.DateTime),
    column('updated_at', sa.DateTime),
    column('context_id', sa.Integer),
    column('scope', sa.String),
)

contexts_table = table(
    'contexts',
    column('id', sa.Integer),
    column('name', sa.String),
    column('description', sa.Text),
    column('related_object_id', sa.Integer),
    column('related_object_type', sa.String),
    column('modified_by_id', sa.Integer),
    column('created_at', sa.DateTime),
    column('updated_at', sa.DateTime),
    column('context_id', sa.Integer),
)


def set_permissions(program_editor_objects):
    program_owner_objects = list(program_editor_objects)
    program_owner_objects.append('UserRole')
    program_owner_create = list(program_owner_objects)
    program_owner_create.append('Audit')

    current_datetime = datetime.now()
    op.execute(roles_table.update().values(
        permissions_json=json.dumps({
            'create': program_owner_create,
            'read': program_owner_objects,
            'update': program_owner_objects,
            'delete': program_owner_objects,
        }),
        updated_at=current_datetime).where(
            roles_table.c.name == 'ProgramOwner'))
    op.execute(roles_table.update().values(
        permissions_json=json.dumps({
            'create': program_editor_objects,
            'read': program_editor_objects,
            'update': program_editor_objects,
            'delete': program_editor_objects,
        }),
        updated_at=current_datetime).where(
            roles_table.c.name == 'ProgramEditor'))
    op.execute(roles_table.update().values(
        permissions_json=json.dumps({
            'create': [],
            'read': program_editor_objects,
            'update': [],
            'delete': [],
        }),
        updated_at=current_datetime).where(
            roles_table.c.name == 'ProgramReader'))


all_tables = [
    'audits',
    'categories',
    'categorizations',
    'contexts',
    'control_controls',
    'control_risks',
    'control_sections',
    'controls',
    'data_assets',
    'directive_controls',
    'directives',
    'documents',
    'events',
    'facilities',
    'helps',
    'markets',
    'meetings',
    'object_controls',
    'object_documents',
    'object_objectives',
    'object_owners',
    'object_people',
    'object_sections',
    'objective_controls',
    'objectives',
    'options',
    'org_groups',
    'people',
    'products',
    'program_controls',
    'program_directives',
    'programs',
    'projects',
    'relationship_types',
    'relationships',
    'requests',
    'responses',
    'risk_risky_attributes',
    'risks',
    'risky_attributes',
    'roles',
    'section_objectives',
    'sections',
    'systems',
    'user_roles',
]

reader_objects = [
    'Categorization',
    'Category',
    'Control',
    'ControlControl',
    'ControlSection',
    'DataAsset',
    'Directive',
    'Contract',
    'Policy',
    'Regulation',
    'Document',
    'Facility',
    'Help',
    'Market',
    'Objective',
    'ObjectControl',
    'ObjectDocument',
    'ObjectObjective',
    'ObjectPerson',
    'ObjectSection',
    'Option',
    'OrgGroup',
    'PopulationSample',
    'Product',
    'ProgramControl',
    'ProgramDirective',
    'Project',
    'Relationship',
    'RelationshipType',
    'Section',
    'SystemOrProcess',
    'System',
    'Process',
    'SystemControl',
    'SystemSystem',
    'ObjectOwner',
    'Person',
    'Program',
    'Role',
]

program_reader_objects = [
    'ObjectDocument',
    'ObjectObjective',
    'ObjectPerson',
    'ObjectSection',
    'Program',
    'ProgramControl',
    'ProgramDirective',
    'Relationship',
]

audit_create_objects = [
    'Request',
    'DocumentationResponse',
    'InterviewResponse',
    'PopulationSampleResponse',
]

audit_owner_create = list(audit_create_objects)
audit_owner_create.append('UserRole')
audit_owner_create.append('Audit')

audit_read_objects = list(audit_create_objects)
audit_read_objects.append('Audit')

auditor_read_objects = ['Audit', 'Request']

audit_update_objects = list(audit_read_objects)


def upgrade():
    # drop Cycle, it doesn't exist
    set_permissions([
        'ObjectDocument',
        'ObjectObjective',
        'ObjectPerson',
        'ObjectSection',
        'Program',
        'ProgramControl',
        'ProgramDirective',
        'Relationship',
    ])
    # create join table for inferred permissions
    # define auditor role
    # define program owner privileges for audit context
    # define program editor privileges for audit context
    # define program reader privileges for audit context
    # set_audit_permissions([
    #     'Audit',
    #     'Request',
    #     'Response',
    # ])

    current_datetime = datetime.now()
    op.bulk_insert(roles_table, [
        {
            'name':
            'AuditorReader',
            'description':
            'A user with Auditor role for a program audit will '
            'also have this role in the default object context so that '
            'the auditor will have access to the objects required to '
            'perform the audit.',
            'permissions_json':
            json.dumps({
                'create': [],
                'read': reader_objects,
                'update': [],
                'delete': [],
            }),
            'scope':
            'System',
            'created_at':
            current_datetime,
            'updated_at':
            current_datetime,
            'context_id':
            None
        },
        {
            'name':
            'AuditorProgramReader',
            'description':
            'A user with Auditor role for a program audit will '
            'also have this role in the program context so that '
            'the auditor will have access to the private program '
            'information and mappings required to perform the audit.',
            'permissions_json':
            json.dumps({
                'create': [],
                'read': program_reader_objects,
                'update': [],
                'delete': [],
            }),
            'scope':
            'Private Program Implied',
            'created_at':
            current_datetime,
            'updated_at':
            current_datetime,
            'context_id':
            None
        },
        {
            'name':
            'ProgramAuditOwner',
            'description':
            'A user with the ProgramOwner role for a private '
            'program will also have this role in the audit context for any '
            'audit created for that program.',
            'permissions_json':
            json.dumps({
                'create': audit_owner_create,
                'read': audit_owner_create,
                'update': audit_update_objects,
                'delete': [],
            }),
            'scope':
            'Audit Implied',
            'created_at':
            current_datetime,
            'updated_at':
            current_datetime,
            'context_id':
            None
        },
        {
            'name':
            'ProgramAuditEditor',
            'description':
            'A user with the ProgramEditor role for a private '
            'program will also have this role in the audit context for any '
            'audit created for that program.',
            'permissions_json':
            json.dumps({
                'create': audit_create_objects,
                'read': audit_read_objects,
                'update': audit_update_objects,
                'delete': [],
            }),
            'scope':
            'Audit Implied',
            'created_at':
            current_datetime,
            'updated_at':
            current_datetime,
            'context_id':
            None
        },
        {
            'name':
            'ProgramAuditReader',
            'description':
            'A user with the ProgramReader role for a private '
            'program will also have this role in the audit context for any '
            'audit created for that program.',
            'permissions_json':
            json.dumps({
                'create': [],
                'read': audit_read_objects,
                'update': [],
                'delete': [],
            }),
            'scope':
            'Audit Implied',
            'created_at':
            current_datetime,
            'updated_at':
            current_datetime,
            'context_id':
            None
        },
        {
            'name':
            'Auditor',
            'description':
            'The permissions required by an auditor to access '
            'relevant resources for the program being audited.',
            'permissions_json':
            json.dumps({
                'create': ['Request'],
                'read': auditor_read_objects,
                'update': ['Request', 'Response'],
                'delete': [],
            }),
            'scope':
            'Audit',
            'created_at':
            current_datetime,
            'updated_at':
            current_datetime,
            'context_id':
            None
        },
    ])

    # Add role implications table
    # Defined within the context of the target so that authorization in the
    # target is a requirement to create the implication.
    op.create_table(
        'role_implications',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('source_context_id', sa.Integer(), nullable=True),
        sa.Column('context_id', sa.Integer(), nullable=True),  # target
        sa.Column('source_role_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),  # target
        sa.Column('modified_by_id', sa.Integer(), nullable=False),
        sa.Column(
            'created_at', sa.DateTime(), default=sa.text('current_timestamp')),
        sa.Column(
            'updated_at',
            sa.DateTime(),
            default=sa.text('current_timestamp'),
            onupdate=sa.text('current_timestamp'),
        ),
        sa.ForeignKeyConstraint(['source_context_id'], ['contexts.id']),
        sa.ForeignKeyConstraint(['context_id'], ['contexts.id']),
        sa.ForeignKeyConstraint(['source_role_id'], ['roles.id']),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id']),
    )
    op.create_unique_constraint(
        'uq_role_implications', 'role_implications',
        ['source_context_id', 'context_id', 'source_role_id', 'role_id'])


def downgrade():
    op.drop_table('role_implications')
