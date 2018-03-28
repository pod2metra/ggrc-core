# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Rename ControlAssessment to Assessment

Revision ID: 17ae137bda7a
Revises: 62f26762d0a
Create Date: 2016-01-14 16:52:23.706170

"""

# revision identifiers, used by Alembic.
revision = '17ae137bda7a'
down_revision = '62f26762d0a'

from alembic import op


def upgrade():
    # Migrate all possible mappings where object_type = 'ControlAssessment'
    objects = {
        "risk_objects": ("object_type", ),
    }
    for key, values in objects.iteritems():
        for value in values:
            sql = """UPDATE {key} SET {value} = 'Assessment'
               WHERE {value} = 'ControlAssessment'"""
            op.execute(sql.format(key=key, value=value))


def downgrade():
    pass
