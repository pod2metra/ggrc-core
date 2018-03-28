# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Check for missing mandatory roles in ACR table and create them.

Create Date: 2017-10-27 12:47:43.403028
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from ggrc.migrations.utils import update_acr

# revision identifiers, used by Alembic.
revision = '1be0dd01f559'
down_revision = '5aa9ec7105d1'

# have Admin role
# no Assessment and Program
RISKS_OWNABLE_MODELS = {
    'Risk',
    'Threat',
}

# have contacts roles
# no Comment and Document
RISKS_MODELS_WITH_CONTACTS = {
    "Risk",
    "Threat",
}

RISKS_NON_EDITABLE_ROLES = {
    "Primary Contacts",
    "Secondary Contacts",
}


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    update_acr.update_ownable_models(RISKS_OWNABLE_MODELS)
    update_acr.update_models_with_contacts(RISKS_MODELS_WITH_CONTACTS,
                                           RISKS_NON_EDITABLE_ROLES)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    pass
