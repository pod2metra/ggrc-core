# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Update Context.related_object where missing

Revision ID: 1d1573d5812f
Revises: 5560713e91b2
Create Date: 2014-05-19 17:59:34.819427

"""

# revision identifiers, used by Alembic.
revision = '1d1573d5812f'
down_revision = '5560713e91b2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column, select, and_

contexts_table = table(
    'contexts',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
    column('related_object_id', sa.Integer),
    column('related_object_type', sa.String),
)

programs_table = table(
    'programs',
    column('id', sa.Integer),
    column('context_id', sa.Integer),
)


def upgrade():
    connection = op.get_bind()

    programs = connection.execute(
        select([programs_table.c.id, programs_table.c.context_id])).fetchall()
    program_ids_by_context = {}
    for program in programs:
        if program.context_id:
            program_ids_by_context[program.context_id] = program.id

    contexts = connection.execute(
        select([
              contexts_table.c.id,
              contexts_table.c.related_object_id
              ])\
            .where(
              and_(
                contexts_table.c.related_object_type == "Program",
                contexts_table.c.related_object_id == None
                ))
        ).fetchall()

    contexts_to_update = []
    for context in contexts:
        if context.related_object_id is None:
            if context.id in program_ids_by_context:
                contexts_to_update.append({
                    "id":
                    context.id,
                    "related_object_id":
                    program_ids_by_context[context.id]
                })

    for context_data in contexts_to_update:
        op.execute(
            contexts_table.update()\
                .values(
                  related_object_id=context_data["related_object_id"]
                  )\
                .where(contexts_table.c.id == context_data["id"]))


def downgrade():
    # Non-reversible migration
    pass
