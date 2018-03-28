# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Clear user roles with invalid context

Create Date: 2017-03-11 14:26:55.133169
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = '3ab8b37b04'
down_revision = '53831d153d8e'


def upgrade():
    """Delete audit user roles from bad audits.

  This will remove all auditors from audits that had the program context
  instead of their own context. In that case there is no way of knowing t
  which audit the any given auditor belonged to in the first place, so from
  security standpoint it is safer to remove those roles and manually add them
  back if needed.
  """
    sql = """
  DELETE user_roles
  FROM user_roles
  JOIN roles as r on user_roles.role_id = r.id
  JOIN contexts as c on user_roles.context_id = c.id
  WHERE
    r.name = "Auditor" AND
    c.related_object_type = "Program"
  """
    op.execute(sql)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
