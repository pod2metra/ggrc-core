# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Migrate contacts to custom_roles

Create Date: 2017-04-26 22:01:48.029793
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from ggrc.migrations.utils.migrate_contacts import migrate_contacts

# revision identifiers, used by Alembic.
revision = '1ac595e94a23'
down_revision = '7371f62ceb3'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    tables = [
        ('AccessGroup', 'access_groups'),
        ('Assessment', 'assessments'),
        ('Clause', 'clauses'),
        ('Contract', 'directives'),
        ('Control', 'controls'),
        ('DataAsset', 'data_assets'),
        ('Facility', 'facilities'),
        ('Issue', 'issues'),
        ('Market', 'markets'),
        ('Objective', 'objectives'),
        ('OrgGroup', 'org_groups'),
        ('Policy', 'directives'),
        ('Process', 'systems'),
        ('Product', 'products'),
        ('Project', 'projects'),
        ('Program', 'programs'),
        ('Regulation', 'directives'),
        ('Section', 'sections'),
        ('Standard', 'directives'),
        ('System', 'systems'),
        ('Vendor', 'vendors'),
    ]
    for type_, table_type in tables:
        migrate_contacts(type_, table_type)
        if type_ == 'Control':
            # Controls have assessors in addition to contacts
            extra_control_mappings = ({
                'name': 'Principal Assignees',
                'column': 'principal_assessor_id',
            }, {
                'name': 'Secondary Assignees',
                'column': 'secondary_assessor_id',
            })
            migrate_contacts(type_, table_type, extra_control_mappings)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    pass
