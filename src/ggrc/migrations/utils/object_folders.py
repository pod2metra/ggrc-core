# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>


INSERT_NON_EXISTS_FOLDERS = """INSERT INTO object_folders
    (folderable_id, folderable_type, folder_id)
select id as folderable_id,
       "{model}" as folderable_type,
       folder
       FROM {table} as t
where folder != "" and not exists (
    select 1
    from object_folders
    where folderable_id = t.id and folderable_type="{model}"
);
"""
UPDATE_SQL = """UPDATE {table} AS wf
LEFT JOIN (
    SELECT folderable_id, folder_id AS folder
    FROM (select distinct folderable_id,
                          folderable_type,
                          folder_id
          from object_folders) as tmp
    WHERE folderable_type = "{model}" group by 1
) as T on T.folderable_id = wf.id
SET wf.folder = COALESCE(T.folder, "");"""

HAVE_TABLE = ('SELECT EXISTS ('
              'SELECT 1 FROM information_schema.tables '
              'WHERE TABLE_NAME = "object_folders" AND '
              'TABLE_SCHEMA = DATABASE()) AS have_table;')


def update(op, table, model):
  """Upgrade database schema and/or data, creating a new revision."""
  # alembic too old and we can't merge and depend revisions from
  # different versions so we have the hack this check if table exists
  res = op.get_bind().execute(HAVE_TABLE)
  if res.fetchone()[0]:
    op.execute(UPDATE_SQL.format(table=table, model=model))


def downgrade(op, table, model):
  """Downgrade database schema and/or data back to the previous revision."""
  op.execute('DELETE FROM object_folders '
             'WHERE folderable_type="{model}"'.format(model=model))
  op.execute(INSERT_NON_EXISTS_FOLDERS.format(table=table, model=model))
