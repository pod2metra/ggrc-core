# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Cleanup Document model

Create Date: 2018-01-15 13:02:12.663009
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '2ac95a7b18fa'
down_revision = '12c716cf3817'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.execute("""
      UPDATE documents
      SET link = ''
      WHERE link IS NULL
  """)
    op.execute("""
      UPDATE documents
      SET title = link
      WHERE title IS NULL
  """)
    op.alter_column(
        'documents',
        'link',
        existing_type=mysql.VARCHAR(length=250),
        nullable=False)
    op.alter_column(
        'documents',
        'title',
        existing_type=mysql.VARCHAR(length=250),
        nullable=False)
    op.drop_column('documents', 'kind_id')
    op.drop_column('documents', 'year_id')
    op.drop_column('documents', 'language_id')


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.add_column('documents',
                  sa.Column(
                      'language_id',
                      mysql.INTEGER(display_width=11),
                      autoincrement=False,
                      nullable=True))
    op.add_column('documents',
                  sa.Column(
                      'year_id',
                      mysql.INTEGER(display_width=11),
                      autoincrement=False,
                      nullable=True))
    op.add_column('documents',
                  sa.Column(
                      'kind_id',
                      mysql.INTEGER(display_width=11),
                      autoincrement=False,
                      nullable=True))
    op.alter_column(
        'documents',
        'title',
        existing_type=mysql.VARCHAR(length=250),
        nullable=True)
    op.alter_column(
        'documents',
        'link',
        existing_type=mysql.VARCHAR(length=250),
        nullable=True)
