# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add unique constraint on attributes table

Create Date: 2017-07-28 11:29:41.606021
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = '191c7cc1fed8'
down_revision = '951213087c6'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.execute("TRUNCATE TABLE attributes")
    op.create_unique_constraint('uq_attributes', 'attributes', [
        'object_id', 'object_type', 'attribute_definition_id',
        'attribute_template_id'
    ])


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_constraint('uq_attributes', 'attributes')
