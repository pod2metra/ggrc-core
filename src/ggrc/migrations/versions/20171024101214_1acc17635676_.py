# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
empty message

Create Date: 2017-10-24 10:12:14.203010
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '1acc17635676'
down_revision = '2ad7783c176'


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  op.create_table(
      'labels',
      sa.Column('id', sa.Integer(), nullable=False),
      sa.Column('name', sa.String(length=250), nullable=False),
      sa.Column('object_type', sa.String(length=250), nullable=True),
      sa.Column('updated_at', sa.DateTime(), nullable=False),
      sa.Column('modified_by_id', sa.Integer(), nullable=True),
      sa.Column('created_at', sa.DateTime(), nullable=False),
      sa.Column('context_id', sa.Integer(), nullable=True),
      sa.ForeignKeyConstraint(['context_id'], ['contexts.id'], ),
      sa.PrimaryKeyConstraint('id'),
      sa.UniqueConstraint('name', 'object_type'),
  )
  op.create_index('fk_labels_contexts',
                  'labels',
                  ['context_id'],
                  unique=False)
  op.create_index('ix_labels_updated_at',
                  'labels',
                  ['updated_at'],
                  unique=False)
  op.create_table(
      'object_label_relations',
      sa.Column('id', sa.Integer(), nullable=False),
      sa.Column('object_id', sa.Integer(), nullable=False),
      sa.Column('object_type', sa.String(length=250), nullable=False),
      sa.Column('label_id', sa.Integer(), nullable=False),
      sa.Column('updated_at', sa.DateTime(), nullable=False),
      sa.Column('modified_by_id', sa.Integer(), nullable=True),
      sa.Column('created_at', sa.DateTime(), nullable=False),
      sa.Column('context_id', sa.Integer(), nullable=True),
      sa.ForeignKeyConstraint(['context_id'], ['contexts.id'], ),
      sa.ForeignKeyConstraint(['label_id'], ['labels.id'], ),
      sa.PrimaryKeyConstraint('id'),
      sa.UniqueConstraint('label_id', 'object_id', 'object_type'),
  )
  op.create_index('fk_object_label_relations_contexts',
                  'object_label_relations',
                  ['context_id'],
                  unique=False)
  op.create_index('idx_object_type_object_idx',
                  'object_label_relations',
                  ['object_type', 'object_id'],
                  unique=False)
  op.create_index('ix_object_label_relations_updated_at',
                  'object_label_relations',
                  ['updated_at'],
                  unique=False)


def downgrade():
  """Downgrade database schema and/or data back to the previous revision."""
  op.drop_index('ix_object_label_relations_updated_at',
                table_name='object_label_relations')
  op.drop_index('idx_object_type_object_idx',
                table_name='object_label_relations')
  op.drop_index('fk_object_label_relations_contexts',
                table_name='object_label_relations')
  op.drop_table('object_label_relations')
  op.drop_index('ix_labels_updated_at',
                table_name='labels')
  op.drop_index('fk_labels_contexts',
                table_name='labels')
  op.drop_table('labels')
