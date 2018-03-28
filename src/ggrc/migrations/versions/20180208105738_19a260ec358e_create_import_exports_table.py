# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Create import_exports table

Create Date: 2018-02-08 10:57:38.888294
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from alembic import op

# revision identifiers, used by Alembic.
revision = '19a260ec358e'
down_revision = '123734a16f69'

IMPORT_EXPORT_STATUSES = [
    'Not Started', 'Analysis', 'Blocked', 'Analysis Failed', 'Stopped',
    'Failed', 'Finished'
]


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.create_table('import_exports',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column(
                        'job_type',
                        sa.Enum('Import', 'Export'),
                        nullable=False),
                    sa.Column(
                        'status',
                        sa.Enum(*IMPORT_EXPORT_STATUSES),
                        nullable=False,
                        default='Not Started'),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('start_at', sa.DateTime(), nullable=True),
                    sa.Column('end_at', sa.DateTime(), nullable=True),
                    sa.Column('created_by_id', sa.Integer(), nullable=False),
                    sa.Column('results', mysql.LONGTEXT(), nullable=True),
                    sa.Column('title', sa.Text(), nullable=True),
                    sa.Column('content', mysql.LONGTEXT(), nullable=True),
                    sa.Column('gdrive_metadata', sa.Text(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.ForeignKeyConstraint(
                        ['created_by_id'],
                        ['people.id'],
                    ))


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_table('import_exports')
