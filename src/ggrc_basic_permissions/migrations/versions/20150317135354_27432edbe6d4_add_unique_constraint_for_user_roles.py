# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""add unique constraint for user roles

Revision ID: 27432edbe6d4
Revises: 3bb32fb65d47
Create Date: 2015-03-17 13:53:54.238347

"""

# revision identifiers, used by Alembic.
revision = '27432edbe6d4'
down_revision = '3bb32fb65d47'

from alembic import op
import sqlalchemy as sa


def upgrade():

    conn = op.get_bind()
    query = 'delete from user_roles where id in (select id from (select count(id) as count, max(id) as id, person_id, role_id, context_id from user_roles group by role_id, context_id, person_id having count > 1) as tmp)'

    res = conn.execute(query)
    while res.rowcount > 0:
        res = conn.execute(query)

    op.create_unique_constraint('unique_role_context_person', 'user_roles',
                                ['role_id', 'context_id', 'person_id'])


def downgrade():
    op.drop_constraint('unique_role_context_person', 'user_roles', 'unique')
