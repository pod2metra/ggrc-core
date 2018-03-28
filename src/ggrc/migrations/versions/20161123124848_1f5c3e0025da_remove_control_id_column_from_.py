# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Remove control_id column from assessments table

Create Date: 2016-11-23 12:48:48.942528
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from datetime import datetime
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = '1f5c3e0025da'
down_revision = '4afe69ce3c38'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    relationships = table("relationships", column('source_id', sa.Integer),
                          column('source_type', sa.String),
                          column('destination_id', sa.Integer),
                          column('destination_type', sa.String),
                          column('created_at', sa.DateTime),
                          column('updated_at', sa.DateTime))
    connection = op.get_bind()
    rows_to_add = connection.execute("""
      SELECT id, control_id from assessments
      WHERE control_id IS NOT NULL
        AND id NOT IN (
          SELECT a.id from relationships AS r
          INNER JOIN assessments AS a
            ON r.source_id=a.control_id
            AND r.destination_id=a.id
          WHERE r.source_type='Control'
            AND r.destination_type='Assessment'
          UNION
          SELECT a.id from relationships AS r
          INNER JOIN assessments AS a
            ON r.source_id=a.id
            AND r.destination_id=a.control_id
          WHERE r.destination_type='Control'
            AND r.source_type='Assessment'
      );
      """)
    now = datetime.now()
    op.bulk_insert(relationships, [{
        'source_id': assessment_id,
        'source_type': 'Assessment',
        'destination_id': control_id,
        'destination_type': 'Control',
        'created_at': now,
        'updated_at': now
    } for (assessment_id, control_id) in rows_to_add])
    op.drop_constraint(
        "fk_control_control_assessment",
        "assessments",
        "foreignkey",
    )
    op.drop_column("assessments", "control_id")


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.add_column("assessments",
                  sa.Column('control_id', sa.Integer, nullable=True))
    op.create_foreign_key("fk_control_control_assessment", "assessments",
                          "controls", ["control_id"], ["id"])
