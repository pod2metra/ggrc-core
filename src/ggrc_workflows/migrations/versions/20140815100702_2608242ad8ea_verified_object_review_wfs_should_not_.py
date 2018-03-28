# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Verified object review wfs should not be current

Revision ID: 2608242ad8ea
Revises: c8263593153
Create Date: 2014-08-15 10:07:02.382613

"""

# revision identifiers, used by Alembic.
revision = '2608242ad8ea'
down_revision = 'c8263593153'

from alembic import op


def upgrade():
    op.execute("""
    UPDATE cycles c, workflows w
    SET is_current=false
    WHERE c.workflow_id=w.id and w.object_approval=true and c.status='Verified'
    """)


def downgrade():
    pass
