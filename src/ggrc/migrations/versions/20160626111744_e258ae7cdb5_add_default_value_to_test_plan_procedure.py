# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add default value to test_plan_procedure

Create Date: 2016-06-26 11:17:44.317908
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = 'e258ae7cdb5'
down_revision = '170e453da661'


def upgrade():
    op.alter_column(
        "assessment_templates", "test_plan_procedure", server_default="0")


def downgrade():
    op.alter_column(
        "assessment_templates", "test_plan_procedure", server_default=None)
