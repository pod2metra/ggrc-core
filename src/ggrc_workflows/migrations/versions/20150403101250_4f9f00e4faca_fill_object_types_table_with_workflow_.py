# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""fill object types table with workflow models

Revision ID: 4f9f00e4faca
Revises: 57cc398ad417
Create Date: 2015-04-03 10:12:50.583661

"""

# Disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=C0103

# revision identifiers, used by Alembic.
revision = '4f9f00e4faca'
down_revision = '8e530ce276a'


def upgrade():
    # This migration has been removed due to remove_object_type_table migration.
    # The object_types table has been removed and there should not be any more
    # references to that table.
    pass


def downgrade():
    pass
