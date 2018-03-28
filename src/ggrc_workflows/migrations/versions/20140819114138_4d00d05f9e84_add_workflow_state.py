# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add workflow state

Revision ID: 4d00d05f9e84
Revises: 2608242ad8ea
Create Date: 2014-08-19 11:41:38.723368

"""

# revision identifiers, used by Alembic.
revision = '4d00d05f9e84'
down_revision = '28f2d0d0362'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(u'workflows',
                  sa.Column(u'status', sa.String(length=250), nullable=True))

    op.add_column(u'workflows',
                  sa.Column('recurrences', sa.Boolean(), nullable=False))

    op.execute("""
    UPDATE workflows
    SET status='Draft', recurrences=false
    """)

    # fix old workflows where frequency is unset
    op.execute("""
    UPDATE workflows
    SET frequency='one_time'
    WHERE frequency IS NULL
    """)

    # workflows with cycles are active
    op.execute("""
    UPDATE workflows w
    INNER JOIN cycles c ON c.workflow_id = w.id
    SET w.status='Active', w.recurrences=(w.frequency != 'one_time')
    """)

    # but one_time workflows with no current cycles are inactive
    op.execute("""
    UPDATE workflows w
    INNER JOIN cycles c ON c.workflow_id = w.id
    SET w.status='Inactive'
    WHERE NOT EXISTS(
      SELECT * FROM cycles c1
      WHERE c1.workflow_id = w.id AND c1.is_current = true
    )
    """)


def downgrade():
    op.drop_column(u'workflows', u'status')
    op.drop_column(u'workflows', u'recurrences')
