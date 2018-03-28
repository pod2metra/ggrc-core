# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Check for missing mandatory roles in ACR table and create them.

Create Date: 2017-10-27 12:47:51.389160
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from ggrc.migrations.utils import update_acr

# revision identifiers, used by Alembic.
revision = '3c095f8ad47'
down_revision = 'fa2f60a53c9'

# have Admin role
# no Assessment and Program
OWNABLE_MODELS = {
    'AccessGroup',
    'Clause',
    'Contract',
    'Control',
    'DataAsset',
    'Facility',
    'Issue',
    'Market',
    'Objective',
    'OrgGroup',
    'Policy',
    'Process',
    'Product',
    'Project',
    'Regulation',
    'Section',
    'Standard',
    'System',
    'Vendor',
    'Comment',
    'Document',
}

# have contacts roles
# no Comment and Document
MODELS_WITH_CONTACTS = {
    "AccessGroup",
    "Assessment",
    "Clause",
    "Contract",
    "Control",
    "DataAsset",
    "Facility",
    "Issue",
    "Market",
    "Objective",
    "OrgGroup",
    "Policy",
    "Process",
    "Product",
    "Project",
    "Program",
    "Regulation",
    "Section",
    "Standard",
    "System",
    "Vendor",
}

NON_EDITABLE_ROLES = {
    "Primary Contacts",
    "Secondary Contacts",
}

NON_EDITABLE_CONTROL_ROLES = {
    "Principal Assignees",
    "Secondary Assignees",
}


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    update_acr.update_ownable_models(OWNABLE_MODELS)
    update_acr.update_models_with_contacts(MODELS_WITH_CONTACTS,
                                           NON_EDITABLE_ROLES)

    for role in NON_EDITABLE_CONTROL_ROLES:
        update_acr.update_acr(
            role,
            "Control",
            non_editable=u"1",
        )


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    pass
