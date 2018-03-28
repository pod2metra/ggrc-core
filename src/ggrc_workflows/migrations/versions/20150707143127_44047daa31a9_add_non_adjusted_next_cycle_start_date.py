# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add non-adjusted next cycle start date

Revision ID: 44047daa31a9
Revises: 1431e7094e26
Create Date: 2015-07-07 14:31:27.780564

"""
# Workaround legacy code which blocks Workflow new attribute addition

# flake8: noqa
# pylint: skip-file

# revision identifiers, used by Alembic.
revision = '44047daa31a9'
down_revision = '4840f4760f4b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('workflows',
                  sa.Column(
                      'non_adjusted_next_cycle_start_date',
                      sa.Date(),
                      nullable=True))
    return


def downgrade():
    op.drop_column('workflows', 'non_adjusted_next_cycle_start_date')
