# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add audit_id FK to AssessmentTemplate

Create Date: 2018-02-09 12:30:55.505996
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '4303f98eec2c'
down_revision = '4e5ef956af94'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.add_column("assessment_templates",
                  sa.Column("audit_id", sa.Integer(), nullable=True))

    op.execute("""
      UPDATE assessment_templates
      JOIN (
          SELECT a.id audit_id, at.id template_id
          FROM audits a
          JOIN relationships r ON
            r.source_id = a.id AND
            r.source_type = 'Audit' AND
            r.destination_type = 'AssessmentTemplate'
          JOIN assessment_templates at ON at.id = r.destination_id

          UNION ALL

          SELECT a.id, at.id
          FROM audits a
          JOIN relationships r ON
            r.destination_id = a.id AND
            r.destination_type = 'Audit' AND
            r.source_type = 'AssessmentTemplate'
          JOIN assessment_templates at ON at.id = r.source_id
      ) temp ON temp.template_id = assessment_templates.id
      SET assessment_templates.audit_id = temp.audit_id
  """)

    op.create_foreign_key(
        "fk_assessment_template_audits",
        "assessment_templates",
        "audits", ["audit_id"], ["id"],
        ondelete='SET NULL')


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_constraint(
        "fk_assessment_template_audits",
        "assessment_templates",
        type_="foreignkey")
    op.drop_column("assessment_templates", "audit_id")
