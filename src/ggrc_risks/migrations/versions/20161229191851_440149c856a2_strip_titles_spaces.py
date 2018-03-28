# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Strip titles' trailing/leading spaces

Create Date: 2016-12-29 19:18:51.436778
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from ggrc.migrations.utils.strip_text_field import strip_spaces_ensure_uniq

# revision identifiers, used by Alembic.
revision = '440149c856a2'
down_revision = '3d2acc8a4425'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    tables = ['risks', 'threats']
    uniq_tables = []
    strip_spaces_ensure_uniq(tables, 'title', uniq_tables)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    pass
