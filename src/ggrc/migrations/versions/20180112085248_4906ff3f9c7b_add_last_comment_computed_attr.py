# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add last comment computed attr

Create Date: 2018-01-12 08:52:48.286089
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name
import datetime

from alembic import op

import sqlalchemy as sa
from sqlalchemy.sql import table, column

revision = '4906ff3f9c7b'
down_revision = '21db8dd549ac'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    attribute_types = table(
        "attribute_types",
        column("attribute_type_id", sa.Integer),
        column("name", sa.String),
        column("field_type", sa.String),
        column("db_column_name", sa.String),
        column("computed", sa.Boolean),
        column("aggregate_function", sa.Text),
        column("created_at", sa.DateTime),
        column("updated_at", sa.DateTime),
    )
    attribute_definitions = table(
        "attribute_definitions",
        column("attribute_definition_id", sa.Integer),
        column("attribute_type_id", sa.Integer),
        column("name", sa.String),
        column("display_name", sa.String),
        column("created_at", sa.DateTime),
        column("updated_at", sa.DateTime),
    )
    object_templates = table(
        "object_templates",
        column("object_template_id", sa.Integer),
        column("object_type_id", sa.Integer),
        column("name", sa.String),
        column("display_name", sa.String),
        column("created_at", sa.DateTime),
        column("updated_at", sa.DateTime),
    )
    attribute_templates = table(
        "attribute_templates",
        column("attribute_template_id", sa.Integer),
        column("attribute_definition_id", sa.Integer),
        column("object_template_id", sa.Integer),
        column("order", sa.Integer),
        column("read_only", sa.Boolean),
        column("created_at", sa.DateTime),
        column("updated_at", sa.DateTime),
        column("help_text", sa.String),
        column("options", sa.String),
        column("default_value", sa.String),
    )

    op.bulk_insert(object_templates, [{
        "object_type_id": 1,
        "name": "Assessment",
        "display_name": "Assessment",
        "created_at": datetime.datetime.now(),
        "updated_at": datetime.datetime.now(),
    }])
    connection = op.get_bind()
    object_template_id = connection.execute(
        sa.select([object_templates.c.object_template_id]).order_by(
            sa.desc("object_template_id"))).fetchone()[0]
    op.bulk_insert(attribute_types,
                   [{
                       "name": "Computed attribute for last comment",
                       "field_type": "value_string",
                       "db_column_name": "last_comment",
                       "computed": True,
                       "aggregate_function": "Comment description last",
                       "created_at": datetime.datetime.now(),
                       "updated_at": datetime.datetime.now(),
                   }])
    attribute_type_id = connection.execute(
        sa.select([attribute_types.c.attribute_type_id]).order_by(
            sa.desc("attribute_type_id"))).fetchone()[0]
    op.bulk_insert(attribute_definitions,
                   [{
                       "attribute_type_id": attribute_type_id,
                       "name": "last_comment",
                       "display_name": "Last Comment",
                       "created_at": datetime.datetime.now(),
                       "updated_at": datetime.datetime.now(),
                   }])
    attribute_definition_id = connection.execute(
        sa.select([attribute_definitions.c.attribute_definition_id]).order_by(
            sa.desc("attribute_definition_id"))).fetchone()[0]
    op.bulk_insert(attribute_templates,
                   [{
                       "attribute_definition_id": attribute_definition_id,
                       "object_template_id": object_template_id,
                       "order": 1,
                       "read_only": True,
                       "created_at": datetime.datetime.now(),
                       "updated_at": datetime.datetime.now(),
                       "help_text": "",
                       "options": "",
                       "default_value": "",
                   }])
    attribute_template_id = connection.execute(
        sa.select([attribute_templates.c.attribute_template_id]).order_by(
            sa.desc("attribute_template_id"))).fetchone()[0]

    connection.execute(
        sa.text("""
          REPLACE INTO attributes (
            object_type,
            object_id,
            source_type,
            source_id,
            source_attr,
            value_datetime,
            value_integer,
            value_string,
            attribute_template_id,
            attribute_definition_id,
            created_at,
            updated_at
          )
          SELECT 'Assessment', tmp2.id, 'Comment', tmp2.last_comment_id,
            'description', NULL, NULL, comments.description,
            :attribute_template_id, :attribute_definition_id, NOW(), NOW()
          FROM (
              SELECT tmp.id, MAX(tmp.comment_id) last_comment_id
              FROM (
                  SELECT a.id, c.id as comment_id
                  FROM assessments a
                  JOIN relationships r ON
                    r.source_id = a.id AND
                    r.source_type = 'Assessment' AND
                    r.destination_type = 'Comment'
                  JOIN comments c ON
                    c.id = r.destination_id

                  UNION ALL

                  SELECT a.id, c.id as comment_id
                  FROM assessments a
                  JOIN relationships r ON
                    r.destination_id = a.id AND
                    r.destination_type = 'Assessment' AND
                    r.source_type = 'Comment'
                  JOIN comments c ON
                    c.id = r.source_id
              ) tmp
              GROUP BY tmp.id
          ) tmp2
          JOIN comments ON comments.id = tmp2.last_comment_id
      """),
        attribute_template_id=attribute_template_id,
        attribute_definition_id=attribute_definition_id)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    attribute_definitions = table(
        "attribute_definitions",
        column("attribute_definition_id", sa.Integer),
        column("attribute_type_id", sa.Integer),
        column("name", sa.String),
    )

    connection = op.get_bind()
    attribute_definition_id = connection.execute(
        sa.select([
            attribute_definitions.c.attribute_definition_id
        ]).where(attribute_definitions.c.name == "last_comment").order_by(
            sa.desc("attribute_definition_id"))).fetchone()[0]

    connection.execute(
        sa.text("""
      DELETE FROM attributes
      WHERE attribute_definition_id = :attribute_definition_id;
  """),
        attribute_definition_id=attribute_definition_id)
    connection.execute(
        sa.text("""
      DELETE FROM attribute_templates
      WHERE attribute_definition_id = :attribute_definition_id;
  """),
        attribute_definition_id=attribute_definition_id)
    connection.execute("""
      DELETE FROM attribute_definitions
      WHERE name = 'last_comment';
  """)
    connection.execute("""
      DELETE FROM attribute_types
      WHERE field_type = 'computed_last_comment';
  """)
    connection.execute("""
      DELETE FROM object_templates
      WHERE name = 'Assessment';
  """)
