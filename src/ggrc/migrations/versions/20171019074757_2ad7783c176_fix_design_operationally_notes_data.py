# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Fix data in the Assessments' fields: design, operationally

Empty strings instead NULL in Nullable columns leads to incorrect behavior
in Assessment status changes.

Create Date: 2017-10-19 07:47:57.404480
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = '2ad7783c176'
down_revision = '5299857cfde0'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.execute("UPDATE assessments SET design='' WHERE design IS NULL;")
    op.execute("UPDATE assessments SET operationally='' "
               "WHERE operationally IS NULL;")
    op.execute("ALTER TABLE assessments "
               "CHANGE design design varchar(250) not NULL default '';")
    op.execute("ALTER TABLE assessments "
               "CHANGE operationally operationally varchar(250) "
               "not NULL default '';")


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.execute("ALTER TABLE assessments "
               "CHANGE design design varchar(250) NULL;")
    op.execute("ALTER TABLE assessments "
               "CHANGE operationally operationally varchar(250) NULL;")
    op.execute("UPDATE assessments SET design=NULL WHERE design='';")
    op.execute("UPDATE assessments SET operationally=NULL "
               "WHERE operationally='';")
