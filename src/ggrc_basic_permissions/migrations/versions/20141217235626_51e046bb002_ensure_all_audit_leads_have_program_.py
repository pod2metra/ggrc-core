# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Ensure all Audit Leads have Program Editor role or better

Revision ID: 51e046bb002
Revises: 581a9621fac1
Create Date: 2014-12-17 23:56:26.323023

"""

# revision identifiers, used by Alembic.
revision = '51e046bb002'
down_revision = '581a9621fac1'

from alembic import op
import sqlalchemy as sa


def upgrade():

    #1: remove programreader roles for assignees (they need to be program editor)
    op.execute("""
      DELETE ur
      FROM user_roles ur, contexts c, audits a, roles r, programs p
      WHERE a.program_id=p.id AND p.context_id=c.id AND ur.context_id=c.id AND ur.role_id=r.id
      AND a.contact_id=ur.person_id
      AND r.name = "ProgramReader"
    """)

    #2: give assignees with no roles in the program ProgramEditor
    op.execute("""
      INSERT INTO user_roles (role_id, created_at, updated_at, context_id, person_id)
      SELECT distinct (SELECT id from roles where name='ProgramEditor') as role_id,
             now() as created_at,
             now() as updated_at,
             p.context_id,
             a.contact_id
      FROM audits a INNER JOIN programs p on a.program_id=p.id
           INNER JOIN contexts c on p.context_id=c.id
           LEFT OUTER JOIN user_roles ur on c.id=ur.context_id and a.contact_id=ur.person_id
      WHERE ur.person_id IS NULL
    """)


def downgrade():
    pass
