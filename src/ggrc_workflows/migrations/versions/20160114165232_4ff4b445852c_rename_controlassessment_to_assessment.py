# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Rename ControlAssessment to Assessment

Revision ID: 4ff4b445852c
Revises: 13e52f6a9deb
Create Date: 2016-01-14 16:52:32.021140

"""

# revision identifiers, used by Alembic.
revision = '4ff4b445852c'
down_revision = '13e52f6a9deb'

from alembic import op


def upgrade():
    # Migrate all possible mappings where object_type = 'ControlAssessment'
    objects = {
        "task_group_objects": ("object_type", ),
        "cycle_task_group_objects": ("object_type", ),
    }
    for key, values in objects.iteritems():
        for value in values:
            sql = """UPDATE {key} SET {value} = 'Assessment'
               WHERE {value} = 'ControlAssessment'"""
            op.execute(sql.format(key=key, value=value))


def downgrade():
    pass
