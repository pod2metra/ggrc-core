# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Assessment titles

Revision ID: 204540106539
Revises: 1894405f14ef
Create Date: 2016-02-23 15:29:16.361412

"""
# Disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=C0103

from alembic import op
from ggrc.models import assessment
from ggrc.migrations.utils.resolve_duplicates import resolve_duplicates

# revision identifiers, used by Alembic.
revision = '204540106539'
down_revision = '1894405f14ef'


def upgrade():
    op.drop_constraint('uq_t_control_assessments', 'assessments', 'unique')


def downgrade():
    resolve_duplicates(assessment.Assessment, 'title', ' ')
    op.create_unique_constraint('uq_t_control_assessments', 'assessments',
                                ['title'])
