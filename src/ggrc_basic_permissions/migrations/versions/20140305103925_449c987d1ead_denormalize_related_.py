# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Denormalize related object types into ContextImplications.

Revision ID: 449c987d1ead
Revises: 3ee919a0daf
Create Date: 2014-03-05 10:39:25.722232

"""

# revision identifiers, used by Alembic.
revision = '449c987d1ead'
down_revision = '3ee919a0daf'

from alembic import op
from datetime import datetime
from sqlalchemy.sql import table, column, select
import sqlalchemy as sa

context_implications_table = table(
    'context_implications',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('source_context_id', sa.Integer),
    column('context_scope', sa.String),
    column('source_context_scope', sa.String),
    column('updated_at', sa.DateTime),
    column('modified_by_id', sa.Integer),
)

contexts_table = table(
    'contexts',
    column('id', sa.Integer),
    column('related_object_id', sa.Integer),
    column('related_object_type', sa.String),
)


def upgrade():
    # Add scoping columns to ContextImplication
    op.add_column('context_implications',
                  sa.Column('context_scope', sa.String(128)))
    op.add_column('context_implications',
                  sa.Column('source_context_scope', sa.String(128)))

    # Copy the related object types from the contexts into the scoping contexts
    # for all implications.
    op.execute(
        context_implications_table.update()\
            .values(context_scope=contexts_table.c.related_object_type)\
            .where(
              context_implications_table.c.context_id == contexts_table.c.id))
    op.execute(
        context_implications_table.update()\
            .values(source_context_scope=contexts_table.c.related_object_type)\
            .where(
              context_implications_table.c.source_context_id ==\
                  contexts_table.c.id))


def downgrade():
    # Drop the scoping columns
    op.drop_column('context_implications', 'context_scope')
    op.drop_column('context_implications', 'source_context_scope')
