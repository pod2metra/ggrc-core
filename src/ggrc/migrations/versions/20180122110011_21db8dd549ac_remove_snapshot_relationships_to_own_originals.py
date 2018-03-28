# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Delete relationships which connect Snapshots to their original objects

Create Date: 2018-01-22 11:00:11.079686
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy.sql.expression import select, join, and_

from alembic import op

# revision identifiers, used by Alembic.
revision = '21db8dd549ac'
down_revision = '2ac95a7b18fa'

relationships = table(
    "relationships",
    column('id', sa.Integer),
    column('source_id', sa.Integer),
    column('source_type', sa.String),
    column('destination_id', sa.Integer),
    column('destination_type', sa.String),
)

snapshots = table(
    "snapshots",
    column('id', sa.Integer),
    column('child_type', sa.String),
)


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    # connection = op.get_bind()
    src_dst_snapshots = join(relationships, snapshots,
                             relationships.c.destination_id == snapshots.c.id)
    sel1 = select([relationships.c.id]).select_from(src_dst_snapshots)\
      .where(and_(snapshots.c.child_type == relationships.c.source_type,  # noqa
             relationships.c.destination_type == "Snapshot"))

    dst_src_snapshots = join(relationships, snapshots,
                             relationships.c.source_id == snapshots.c.id)
    sel2 = select([relationships.c.id]).select_from(dst_src_snapshots)\
      .where(and_(snapshots.c.child_type == relationships.c.destination_type,  # noqa
             relationships.c.source_type == "Snapshot"))

    op.execute(relationships.delete().where(
        relationships.c.id.in_(
            sel1.union_all(sel2).alias("delete_it").select())))


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    pass
