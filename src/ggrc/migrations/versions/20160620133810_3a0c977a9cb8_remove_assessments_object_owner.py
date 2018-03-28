# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Remove Assessments object_owner

Create Date: 2016-06-20 13:38:10.780081
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '3a0c977a9cb8'
down_revision = 'e258ae7cdb5'


def upgrade():
    """Replace Assessment owners with Creator role."""
    op.execute("""
    INSERT INTO relationships (created_at, updated_at,
      source_type, source_id, destination_type, destination_id)
    SELECT created_at, updated_at,
           'Assessment', ownable_id, 'Person', person_id
    FROM object_owners
    WHERE ownable_type = 'Assessment' AND NOT EXISTS (
      SELECT 1
      FROM relationships
      WHERE (
        source_type = 'Assessment' AND source_id = ownable_id AND
        destination_type = 'Person' AND destination_id = person_id
      ) UNION
      SELECT 1
      FROM relationships WHERE (
        source_type='Person' AND source_id = person_id AND
        destination_type ='Assessment' AND destination_id = ownable_id
      )
    );
  """)

    conn = op.get_bind()
    relationship_ids = [
        row[0] for row in conn.execute(
            text("""
     SELECT relationships.id
     FROM relationships
     JOIN object_owners ON (
       source_type = 'Assessment' AND ownable_type = 'Assessment' AND
       source_id = ownable_id AND
       destination_type = 'Person' and destination_id = person_id
     ) WHERE NOT EXISTS (
       SELECT 1
       FROM relationship_attrs
       WHERE relationship_id = relationships.id
       AND attr_value LIKE "%Creator%"
     )
     UNION
     SELECT relationships.id
     FROM relationships
     JOIN object_owners ON (
       destination_type = 'Assessment' AND ownable_type = 'Assessment' AND
       destination_id = ownable_id AND
       source_type = 'Person' and source_id = person_id
     ) WHERE NOT EXISTS (
       SELECT 1
       FROM relationship_attrs
       WHERE relationship_id = relationships.id
       AND attr_value LIKE "%Creator%"
     );
  """))
    ]

    # doing two statements per relationships but this is generally safe because
    # there will usually only be a handful of such relationships
    for rid in relationship_ids:
        attrs = list(
            conn.execute(
                text("""
      SELECT id, attr_value
      FROM relationship_attrs
      WHERE relationship_id = :rid
      AND attr_name = 'AssigneeType';
    """),
                rid=rid))
        if attrs:
            for attr_id, attr_value in attrs:
                new_value = ','.join(
                    set(attr_value.split(',')) | set(['Creator']))
                conn.execute(
                    text("""
          UPDATE relationship_attrs
          SET attr_value = :new_value
          WHERE id = :attr_id;
        """),
                    attr_id=attr_id,
                    new_value=new_value).close()
        else:
            conn.execute(
                text("""
        INSERT INTO relationship_attrs (relationship_id, attr_name, attr_value)
        VALUES (:rid, 'Assignee', 'Creator');
      """),
                rid=rid).close()

    op.execute("""
      DELETE FROM object_owners
      WHERE ownable_type = "Assessment";
  """)


def downgrade():
    """Do nothing as we cannot bring back the data."""
    pass
