# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add labels table

Create Date: 2017-11-28 14:59:26.839363
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import datetime
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '1b4c9fd11de1'
down_revision = '4f01efeeba4d'

DEFAULT_LABELS = [
    'Needs Discussion', 'Needs Rework', 'Followup', 'Auditor Pulls Evidence'
]


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""

    labels_columns = [
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=250), nullable=False),
        sa.Column('object_type', sa.String(length=250), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('modified_by_id', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('context_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['context_id'],
            ['contexts.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'object_type')
    ]

    op.create_table('labels', *labels_columns)

    op.create_table('object_labels',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('label_id', sa.Integer, nullable=False),
                    sa.Column('object_id', sa.Integer, nullable=False),
                    sa.Column(
                        'object_type', sa.String(length=250), nullable=False),
                    sa.Column('modified_by_id', sa.Integer(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('context_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['context_id'],
                        ['contexts.id'],
                    ), sa.ForeignKeyConstraint(
                        ['label_id'],
                        ['labels.id'],
                    ), sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('label_id', 'object_id',
                                        'object_type'))

    # insert default values
    labels = sa.sql.table('labels', *labels_columns[:-3])
    now = datetime.datetime.now()

    op.bulk_insert(labels, [{
        'name': name,
        'object_type': 'Assessment',
        'created_at': now,
        'updated_at': now,
    } for name in DEFAULT_LABELS])


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_table('object_labels')
    op.drop_table('labels')
