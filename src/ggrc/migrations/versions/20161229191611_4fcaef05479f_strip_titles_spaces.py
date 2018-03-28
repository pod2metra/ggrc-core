# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Strip titles' trailing/leading spaces

Create Date: 2016-12-29 19:16:11.268293
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from ggrc.migrations.utils.strip_text_field import strip_spaces_ensure_uniq

# revision identifiers, used by Alembic.
revision = '4fcaef05479f'
down_revision = '587e41a1593d'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    tables = [
        'access_groups', 'assessments', 'assessment_templates', 'audits',
        'clauses', 'controls', 'custom_attribute_definitions', 'data_assets',
        'directives', 'documents', 'facilities', 'helps', 'issues', 'markets',
        'meetings', 'objectives', 'options', 'org_groups', 'products',
        'programs', 'projects', 'requests', 'sections', 'systems', 'vendors'
    ]
    uniq_tables = [
        'access_groups', 'audits', 'clauses', 'controls',
        'custom_attribute_definitions', 'data_assets', 'directives',
        'documents', 'facilities', 'issues', 'markets', 'meetings',
        'objectives', 'options', 'org_groups', 'products', 'programs',
        'projects', 'sections', 'systems', 'vendors'
    ]
    strip_spaces_ensure_uniq(tables, 'title', uniq_tables)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    pass
