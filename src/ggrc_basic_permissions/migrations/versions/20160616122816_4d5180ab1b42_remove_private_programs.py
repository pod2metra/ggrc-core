# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Remove private programs

Create Date: 2016-06-16 12:28:16.744816
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '4d5180ab1b42'
down_revision = '5208a8371512'


def upgrade():
    """Add context implications for private programs and drop the column"""

    op.execute("""
      INSERT INTO context_implications (
        context_id, source_context_id,
        context_scope, source_context_scope,
        created_at, updated_at
      ) SELECT context_id, null, 'Program', null, now(), now()
      FROM programs
      WHERE programs.private IS TRUE
      AND NOT EXISTS (
        SELECT 1
        FROM context_implications
        WHERE context_implications.context_id = programs.context_id
        AND context_implications.source_context_id IS NULL
      );
      """)
    op.drop_column('programs', 'private')


def downgrade():
    """Add private column to programs but keep them all public."""
    op.add_column('programs',
                  sa.Column(
                      'private',
                      mysql.TINYINT(display_width=1),
                      autoincrement=False,
                      nullable=False))
