# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Create dummy revisions needed for Audit snapshot migration


This helper is used by the following migrations:

* ggrc.migrations.versions.20170105231037_579239d161e1
* ggrc_risks.versions.20170106010351_4bbb12265994
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from sqlalchemy.sql import text

from alembic import op

from ggrc.models import all_models

DIRECTIVES = {
    "Policy",
    "Regulation",
    "Standard",
    "Contract",
}

SYS_OR_PROC = {
    "System",
    "Process",
}


def _print_missing_counts(objects):
    """Print counts of missing revisions for all objects.

  Args:
    objects: list of model names
  Returns:
    sum of all missing revision counts.
  """
    connection = op.get_bind()
    sum_counts = 0
    for obj_name in objects:
        if obj_name in SYS_OR_PROC:
            counts = connection.execute(
                text("""
        SELECT count(*)
        FROM systems
        WHERE is_biz_process = :proc
        AND id NOT IN (
          SELECT resource_id
          FROM revisions
          WHERE resource_type = :val
        )
        """),
                proc=1 if obj_name == "Process" else 0,
                val=obj_name).fetchone()

        elif obj_name in DIRECTIVES:
            counts = connection.execute(
                text("""
        SELECT count(*)
        FROM directives
        WHERE meta_kind = :val
        AND id NOT IN (
          SELECT resource_id
          FROM revisions
          WHERE resource_type = :val
        )
        """),
                val=obj_name).fetchone()

        else:
            model = getattr(all_models, obj_name, None)
            if not model:
                continue
            table_name = model._inflector.table_plural  # pylint: disable=W0212

            counts = connection.execute(
                text("""
        SELECT count(*)
        FROM {}
        WHERE id NOT IN (
          SELECT resource_id
          FROM revisions
          WHERE resource_type = :val
        )
        """.format(table_name)),
                val=obj_name).fetchone()
        print "{:<20}: {:>4}".format(obj_name, counts[0])
        sum_counts += counts[0]
    return sum_counts


def _insert_missing_objects(objects):
    """Insert missing revisions for given objects.

  Args:
    objects: List of model names for which we want to create missing revisions.
  """
    event_id = _create_bulk_event()
    connection = op.get_bind()
    for obj_name in objects:
        if obj_name in SYS_OR_PROC:
            connection.execute(
                text("""
              INSERT INTO revisions(
                  resource_id,
                  resource_type,
                  event_id,
                  modified_by_id,
                  action,
                  content,
                  created_at,
                  updated_at
              )
              SELECT
                  id,
                  '{obj_name}',
                  {event_id},
                  modified_by_id,
                  'created',
                  '{{}}',
                  now(),
                  now()
              FROM systems
              WHERE is_biz_process = {proc}
              AND id NOT IN (
                SELECT resource_id
                FROM revisions
                WHERE resource_type = '{obj_name}'
              )
          """.format(
                    obj_name=obj_name,
                    event_id=event_id,
                    proc=1 if obj_name == "Process" else 0,
                )), )

        elif obj_name in DIRECTIVES:
            connection.execute(
                text("""
              INSERT INTO revisions(
                  resource_id,
                  resource_type,
                  event_id,
                  modified_by_id,
                  action,
                  content,
                  created_at,
                  updated_at
              )
              SELECT
                  id,
                  '{obj_name}',
                  {event_id},
                  modified_by_id,
                  'created',
                  '{{}}',
                  now(),
                  now()
              FROM directives
              WHERE meta_kind = '{obj_name}'
              AND id NOT IN (
                SELECT resource_id
                FROM revisions
                WHERE resource_type = '{obj_name}'
              )
          """.format(
                    obj_name=obj_name,
                    event_id=event_id,
                )), )

        else:
            model = getattr(all_models, obj_name, None)
            table_name = model._inflector.table_plural  # pylint: disable=W0212

            connection.execute(
                text("""
              INSERT INTO revisions(
                  resource_id,
                  resource_type,
                  event_id,
                  modified_by_id,
                  action,
                  content,
                  created_at,
                  updated_at
              )
              SELECT
                  id,
                  '{obj_name}',
                  {event_id},
                  modified_by_id,
                  'created',
                  '{{}}',
                  now(),
                  now()
              FROM {table_name}
              WHERE id NOT IN (
                SELECT resource_id
                FROM revisions
                WHERE resource_type = '{obj_name}'
              )
          """.format(
                    table_name=table_name,
                    obj_name=obj_name,
                    event_id=event_id,
                )), )


def _create_bulk_event():
    """Create a dummy event to map the missing revisions to.

  Returns:
    ID of the created event.
  """
    connection = op.get_bind()
    # TODO: add modified_by_id
    connection.execute("INSERT INTO events (action, created_at, updated_at) "
                       "VALUES ('BULK', now(), now())")
    return connection.execute("SELECT LAST_INSERT_ID()").fetchall()[0][0]


def _filter_objects(objects):
    """Remove all objects that do not have a table.

  Args:
    objects: list of Models names for which we want to create revisions
  Returns:
    list of Models names that already have a table created.
  """
    connection = op.get_bind()
    tables_query = connection.execute("SHOW TABLES").fetchall()
    existing_tables = {row[0] for row in tables_query}
    existing_models = {
        model.__name__
        for model in all_models.all_models
        if model.__tablename__ in existing_tables
    }

    fake_objects = [name for name in objects if name not in existing_models]
    if fake_objects:
        print "Following objects not found:", fake_objects

    return [name for name in objects if name in existing_models]


def handle_objects(objects):
    """Create missing revisions for all listed objects.

  Args:
    objects: List of model names for which we want to create missing revisions.
  """

    existing_objects = _filter_objects(objects)

    print "#" * 80
    sum_counts = _print_missing_counts(existing_objects)
    print "#" * 80

    if not sum_counts:
        # No missing revisions, we can safely return
        return

    _insert_missing_objects(existing_objects)

    _print_missing_counts(existing_objects)
    print "#" * 80
