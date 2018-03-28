# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Fix audit context

Create Date: 2017-03-07 13:17:17.472314
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = '1a5ec1ed04af'
down_revision = '3f615f3b5192'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    # pylint: disable=too-many-statements

    # clear bad audit ids, clearing instead of just fixing the bad audit ids will
    # make it easier to propagate this change to all of its related objects that
    # also have an invalid context id.

    # Clear audit_
    sql = """
    UPDATE audits AS au
    LEFT JOIN contexts AS c ON
      au.context_id = c.id
    SET au.context_id = NULL
    WHERE c.related_object_type != "Audit"
  """
    op.execute(sql)

    # Clear all bad contexts from any audit related object.

    # Clear snapshot_
    sql = """
    UPDATE snapshots AS s
    JOIN audits AS au ON
      s.parent_id = au.id AND
      s.parent_type = "Audit"
    SET s.context_id = NULL
    WHERE au.context_id IS NULL
  """
    op.execute(sql)

    # Clear issue_
    sql = """
  UPDATE issues AS i
    JOIN relationships AS r ON r.source_id = i.id
     AND r.source_type = 'Issue' AND r.destination_type = 'Audit'
    JOIN audits AS au ON r.destination_id = au.id
     SET i.context_id = NULL
   WHERE au.context_id is NULL;
  """
    op.execute(sql)

    sql = """
  UPDATE issues AS i
    JOIN relationships AS r ON r.destination_id = i.id
     AND r.destination_type = 'Issue' AND r.source_type = 'Audit'
    JOIN audits AS au ON r.source_id = au.id
     SET i.context_id = NULL
   WHERE au.context_id is NULL
  """
    op.execute(sql)

    # Clear assessment_
    sql = """
  UPDATE assessments AS a
    JOIN relationships AS r ON r.source_id = a.id
     AND r.source_type = 'Assessment' AND r.destination_type = 'Audit'
    JOIN audits AS au ON r.destination_id = au.id
     SET a.context_id = NULL
   WHERE au.context_id is NULL;
  """
    op.execute(sql)

    sql = """
  UPDATE assessments AS a
    JOIN relationships AS r ON r.destination_id = a.id
     AND r.destination_type = 'Assessment' AND r.source_type = 'Audit'
    JOIN audits AS au ON r.source_id = au.id
     SET a.context_id = NULL
   WHERE au.context_id is NULL
  """
    op.execute(sql)

    # Clear object_document
    sql = """
  UPDATE object_documents AS od
    JOIN assessments AS a ON od.documentable_id = a.id
     SET od.context_id = NULL
   WHERE documentable_type = 'Assessment' AND a.context_id IS NULL;
  """
    op.execute(sql)

    sql = """
  UPDATE object_documents AS od
    JOIN issues AS i ON od.documentable_id = i.id
     SET od.context_id = NULL
   WHERE documentable_type = 'Issue' AND i.context_id IS NULL;
  """
    op.execute(sql)

    # Clear document_
    sql = """
  UPDATE documents AS d
    JOIN object_documents AS od ON od.document_id = d.id
     AND od.documentable_type in ("Assessment", "Issue")
     SET d.context_id = NULL
   WHERE od.context_id IS NULL
  """
    op.execute(sql)

    sql = """
  UPDATE documents AS d
    JOIN relationships AS r ON
        r.source_id = d.id AND
        r.source_type = "Document" AND
        r.destination_type = "Assessment"
    JOIN assessments AS a ON
        r.destination_id = a.id
     SET d.context_id = NULL
   WHERE a.context_id IS NULL
  """
    op.execute(sql)

    sql = """
  UPDATE documents AS d
    JOIN relationships AS r ON
        r.destination_id = d.id AND
        r.destination_type = "Document" AND
        r.source_type = "Assessment"
    JOIN assessments AS a ON
        r.source_id = a.id
     SET d.context_id = NULL
   WHERE a.context_id IS NULL
  """
    op.execute(sql)

    # Clear assessment_template
    sql = """
  UPDATE assessment_templates AS at
    JOIN relationships AS r ON
        r.source_id = at.id AND
        r.source_type = "AssessmentTemplate" AND
        r.destination_type = "Audit"
    JOIN audits AS au ON
        r.destination_id = au.id
     SET at.context_id = NULL
   WHERE au.context_id IS NULL
  """
    op.execute(sql)

    sql = """
  UPDATE assessment_templates AS at
    JOIN relationships AS r ON
        r.destination_id = at.id AND
        r.destination_type = "AssessmentTemplate" AND
        r.source_type = "Audit"
    JOIN audits AS au ON
        r.source_id = au.id
     SET at.context_id = NULL
   WHERE au.context_id IS NULL
  """
    op.execute(sql)

    #############################################################################
    # Now we will apply the audit context fix and propagate the change to all of
    # its related objects
    #############################################################################

    # Set audit_
    sql = """
    UPDATE audits AS au
    JOIN contexts AS c ON
      au.id = c.related_object_id AND
      c.related_object_type = "Audit"
    SET au.context_id = c.id
    where au.context_id is NULL
  """
    op.execute(sql)

    # Set snapshot_
    sql = """
    UPDATE snapshots AS s
      JOIN audits AS au ON
           s.parent_id = au.id AND
           s.parent_type = "Audit"
       SET s.context_id = au.context_id
     WHERE s.context_id IS NULL
  """
    op.execute(sql)

    # Set issue_
    sql = """
  UPDATE issues AS i
    JOIN relationships AS r ON r.source_id = i.id
     AND r.source_type = 'Issue' AND r.destination_type = 'Audit'
    JOIN audits AS au ON r.destination_id = au.id
     SET i.context_id = au.context_id
   WHERE i.context_id is NULL;
  """
    op.execute(sql)

    sql = """
  UPDATE issues AS i
    JOIN relationships AS r ON r.destination_id = i.id
     AND r.destination_type = 'Issue' AND r.source_type = 'Audit'
    JOIN audits AS au ON r.source_id = au.id
     SET i.context_id = au.context_id
   WHERE i.context_id is NULL;
  """
    op.execute(sql)

    # Set assessment_
    sql = """
  UPDATE assessments AS a
    JOIN relationships AS r ON r.source_id = a.id
     AND r.source_type = 'Assessment' AND r.destination_type = 'Audit'
    JOIN audits AS au ON r.destination_id = au.id
     SET a.context_id = au.context_id
   WHERE a.context_id is NULL;
  """
    op.execute(sql)

    sql = """
  UPDATE assessments AS a
    JOIN relationships AS r ON r.destination_id = a.id
     AND r.destination_type = 'Assessment' AND r.source_type = 'Audit'
    JOIN audits AS au ON r.source_id = au.id
     SET a.context_id = au.context_id
   WHERE a.context_id is NULL;
  """
    op.execute(sql)

    # Set object_document
    sql = """
  UPDATE object_documents AS od
    JOIN assessments AS a ON od.documentable_id = a.id
     SET od.context_id = a.context_id
   WHERE documentable_type = 'Assessment' AND od.context_id IS NULL;
  """
    op.execute(sql)

    sql = """
  UPDATE object_documents AS od
    JOIN issues AS i ON od.documentable_id = i.id
     SET od.context_id = i.context_id
   WHERE documentable_type = 'Issue' AND od.context_id IS NULL;
  """
    op.execute(sql)

    # Set document_
    sql = """
  UPDATE documents AS d
    JOIN object_documents AS od ON od.document_id = d.id
     AND od.documentable_type in ("Assessment", "Issue")
     SET d.context_id = od.context_id
   WHERE d.context_id IS NULL
  """
    op.execute(sql)

    sql = """
  UPDATE documents AS d
    JOIN relationships AS r ON
        r.source_id = d.id AND
        r.source_type = "Document" AND
        r.destination_type = "Assessment"
    JOIN assessments AS a ON
        r.destination_id = a.id
     SET d.context_id = a.context_id
   WHERE d.context_id IS NULL
  """
    op.execute(sql)

    sql = """
  UPDATE documents AS d
    JOIN relationships AS r ON
        r.destination_id = d.id AND
        r.destination_type = "Document" AND
        r.source_type = "Assessment"
    JOIN assessments AS a ON
        r.source_id = a.id
     SET d.context_id = a.context_id
   WHERE d.context_id IS NULL
  """
    op.execute(sql)

    # Set assessment_template
    sql = """
  UPDATE assessment_templates AS at
    JOIN relationships AS r ON
        r.source_id = at.id AND
        r.source_type = "AssessmentTemplate" AND
        r.destination_type = "Audit"
    JOIN audits AS au ON
        r.destination_id = au.id
     SET at.context_id = au.context_id
   WHERE at.context_id IS NULL
  """
    op.execute(sql)

    sql = """
  UPDATE assessment_templates AS at
    JOIN relationships AS r ON
        r.destination_id = at.id AND
        r.destination_type = "AssessmentTemplate" AND
        r.source_type = "Audit"
    JOIN audits AS au ON
        r.source_id = au.id
     SET at.context_id = au.context_id
   WHERE at.context_id IS NULL
  """
    op.execute(sql)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    pass
