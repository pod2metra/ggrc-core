# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Remove bad CA names

Create Date: 2016-10-20 12:56:20.500665
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column, select

# revision identifiers, used by Alembic.
revision = "1db61b597d2d"
down_revision = "53206b20c12b"

CAD = table(
    "custom_attribute_definitions",
    column("id", sa.Integer),
    column("title", sa.String),
    column("definition_id", sa.Integer),
    column("definition_type", sa.String),
)


def _update_at_cad_titles(old_titles, new_titles):
    """Update Assessment template CAD titles."""
    for old, new in zip(old_titles, new_titles):
        op.execute(CAD.update().where(CAD.c.title == old)
                   .where(CAD.c.definition_type == "assessment_template")
                   .values(title=new))


def upgrade():
    """Upgrade database schema and/or data, creating a new revision.

  The global CAD titles to be replaced can be found with the sql statement:
    SELECT title
    FROM custom_attribute_definitions
    WHERE definition_type = "assessment_template"
    AND title IN (
        SELECT DISTINCT(title)
        FROM custom_attribute_definitions
        WHERE definition_type = "assessment"
        AND definition_id IS NULL
    )
  """
    connection = op.get_bind()

    assessment_global_titles = select([CAD.c.title])\
        .where(CAD.c.definition_type == "assessment")\
        .where(CAD.c.definition_id.is_(None))
    bad_rows_sql = select([CAD.c.title])\
        .where(CAD.c.definition_type == "assessment_template")\
        .where(CAD.c.title.in_(assessment_global_titles))
    bad_rows = connection.execute(bad_rows_sql).fetchall()
    bad_titles = [row.title for row in bad_rows]

    if not bad_titles:
        return
    max_tries = int(
        connection.execute("SELECT count(id) FROM custom_attribute_definitions"
                           ).first()[0]) + 1

    for counter in range(1, max_tries):
        new_titles = [
            u"{} ({})".format(title, counter) for title in bad_titles
        ]
        collisions = connection.execute(CAD.select().where(
            CAD.c.title.in_(new_titles))).fetchall()
        if not collisions:
            _update_at_cad_titles(bad_titles, new_titles)
            break


def downgrade():
    """Ignore downgrade function.

  Fixing title names can't be reversed so there is nothing to do here.
  """
