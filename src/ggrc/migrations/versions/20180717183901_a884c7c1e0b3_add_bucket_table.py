# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
add bucket table

Create Date: 2018-07-17 18:39:01.629373
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a884c7c1e0b3'
down_revision = '054d15be7a29'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.create_table('bucket_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key_obj_type', sa.String(length=250), nullable=False),
    sa.Column('key_obj_id', sa.Integer(), nullable=False),
    sa.Column('scoped_obj_type', sa.String(length=250), nullable=False),
    sa.Column('scoped_obj_id', sa.Integer(), nullable=False),
    sa.Column('parent_relationship_id', sa.Integer(), nullable=False),
    sa.Column('parent_bucket_id', sa.Integer(), nullable=True),
    sa.Column('path', sa.String(length=250 * 10), nullable=False),
    sa.ForeignKeyConstraint(['parent_bucket_id'],
                            ['bucket_items.id'],
                            ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['parent_relationship_id'],
                            ['relationships.id'],
                            ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key_obj_id',
                        'key_obj_type',
                        'scoped_obj_id',
                        'scoped_obj_type',
                        'parent_relationship_id',
                        'parent_bucket_id',
                        'path')
    )
    op.create_index('ix_scoped_obj',
                    'bucket_items',
                    ['scoped_obj_type', 'scoped_obj_id'],
                    unique=False)
    # ### end Alembic commands ###

def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_index('ix_scoped_obj', table_name='bucket_items')
    op.drop_table('bucket_items')
    # ### end Alembic commands ###
