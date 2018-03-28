# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Add ContextImplication from Program context to Common context

Revision ID: 387cf5a9a3ad
Revises: 449c987d1ead
Create Date: 2014-03-18 20:36:51.122756

"""

# revision identifiers, used by Alembic.
revision = '387cf5a9a3ad'
down_revision = '449c987d1ead'

from alembic import op, context
from datetime import datetime
from sqlalchemy.sql import table, column, select, insert, and_
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
    connection = op.get_bind()

    # Find all "Program" contexts
    select_context_ids = select([contexts_table.c.id])\
        .where(contexts_table.c.related_object_type == "Program")\
        .distinct()
    context_ids = connection.execute(select_context_ids).fetchall()

    # Find all ContextImplications matching our parameters
    #   (these would have been created by referencing RoleImplication objects)
    select_context_ids_to_skip = select(
        [context_implications_table.c.source_context_id]).\
            where(
              and_(
                context_implications_table.c.source_context_scope == "Program",
                context_implications_table.c.context_scope == None,
                context_implications_table.c.context_id == None))
    context_ids_to_skip = \
        connection.execute(select_context_ids_to_skip).fetchall()

    # If a matching ContextImplication exists, don't create another
    context_ids = [x for (x, ) in context_ids]
    context_ids_to_skip = [x for (x, ) in context_ids_to_skip]
    context_ids = set(context_ids) - set(context_ids_to_skip)

    # Construct the rows to be inserted
    current_datetime = datetime.now()
    values = []
    for context_id in context_ids:
        values.append({
            'source_context_id': context_id,
            'source_context_scope': 'Program',
            'context_id': None,
            'context_scope': None,
            'created_at': current_datetime,
            'updated_at': current_datetime,
        })

    if len(values) > 0:
        op.bulk_insert(context_implications_table, values)


def downgrade():
    # Some of these ContextImplications already exist, so don't remove any

    #op.execute(context_implications_table.delete().where(
    #  and_(
    #    context_implications_table.c.source_context_scope == 'Program',
    #    context_implications_table.c.context_scope == None,
    #  context_implications_table.c.context_id == None)))
    pass
