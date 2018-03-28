# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Remove relationships related to deleted response objects

Create Date: 2016-05-10 12:25:26.383695
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = '44ebc240800b'
down_revision = '3715694bd315'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.execute("""
      DELETE FROM relationships
      WHERE source_type IN
        ("Response", "DocumentationResponse", "InterviewResponse",
         "PopulationSampleResponse")
        OR destination_type IN
          ("Response", "DocumentationResponse", "InterviewResponse",
           "PopulationSampleResponse")
      """)
    op.execute("""
      DELETE FROM object_documents
      WHERE documentable_type IN
        ("Response", "DocumentationResponse", "InterviewResponse",
         "PopulationSampleResponse")
      """)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    pass
