# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Replace event action enum value

Create Date: 2016-09-05 12:28:05.060667
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from sqlalchemy.sql import and_
from sqlalchemy.sql import column
from sqlalchemy.sql import table
from sqlalchemy.sql import select

from sqlalchemy.sql.expression import bindparam

from alembic import op

# revision identifiers, used by Alembic.
revision = "4450e7d1e441"
down_revision = "173b800a28f3"

events_table = table(
    "events",
    column("id"),
    column("action"),
    column("resource_type"),
)


def upgrade():  # pylint: disable=too-many-locals
    """Upgrade events table to new bulk format.

  The data migration takes 3 steps, composing from two main parts - primary and
  secondary. Primary makes the "core" data migration (1. step), while the
  secondary fixes currently corrupted data (GET and BULK).

  1. step: Migrate events.action = "IMPORT" to "BULK"

  2. step: For a while we didn't have GET in events.action enum so the values
  that got inserted had action = "". We recognize these as action = "" and
  resource_type IS NOT NULL.

  3. step: Due to missing data migration that migrated IMPORT to BULK without
  first changing values we convert event.action = "" AND
  event.resource_type IS NULL to "BULK"
  """
    connection = op.get_bind()
    update_sql = events_table.update().where(
        events_table.c.id == bindparam("_id"))

    # 1st step
    import_sql = select(
        [events_table]).where(events_table.c.action == "IMPORT")
    result_import_sql = connection.execute(import_sql).fetchall()

    import_ids = [{"_id": _id} for _id, _, _ in result_import_sql]
    update_import_sql = update_sql.values(action="BULK")

    if import_ids:
        connection.execute(update_import_sql, import_ids)

    # 2nd step
    missing_gets_sql = select([events_table]).where(
        and_(events_table.c.action == "",
             events_table.c.resource_type.isnot(None)))
    result_missing_gets = connection.execute(missing_gets_sql).fetchall()
    gets_ids = [{"_id": _id} for _id, _, _ in result_missing_gets]
    update_missing_gets_sql = update_sql.values(action="GET")
    if gets_ids:
        connection.execute(update_missing_gets_sql, gets_ids)

    # 3rd step
    missing_bulks_sql = select([events_table]).where(
        and_(events_table.c.action == "",
             events_table.c.resource_type.is_(None)))
    result_missing_bulks = connection.execute(missing_bulks_sql).fetchall()
    bulks_ids = [{"_id": _id} for _id, _, _ in result_missing_bulks]
    update_missing_bulks_sql = update_sql.values(action="BULK")
    if bulks_ids:
        connection.execute(update_missing_bulks_sql, bulks_ids)

    op.alter_column(
        "events",
        "action",
        type_=sa.Enum(u"POST", u"PUT", u"DELETE", u"BULK", u"GET"),
        existing_type=sa.Enum(u"POST", u"PUT", u"DELETE", u"IMPORT", u"BULK",
                              u"GET"),
        nullable=False)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    connection = op.get_bind()
    op.alter_column(
        "events",
        "action",
        type_=sa.Enum(u"POST", u"PUT", u"DELETE", "IMPORT", u"BULK", u"GET"),
        existing_type=sa.Enum(u"POST", u"PUT", u"DELETE", u"BULK", u"GET"),
        nullable=False)

    bulk_sql = select([events_table]).where(events_table.c.action == "BULK")
    result_bulk_sql = connection.execute(bulk_sql).fetchall()

    update_sql = events_table.update().where(
        events_table.c.id == bindparam("_id"))

    bulk_ids = [{"_id": _id} for _id, _, _ in result_bulk_sql]
    update_import_sql = update_sql.values(action="IMPORT")

    if bulk_ids:
        connection.execute(update_import_sql, bulk_ids)
