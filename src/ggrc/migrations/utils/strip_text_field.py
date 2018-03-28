# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Strip trailing spaces from text field

This helper is used by the following migrations:

* ggrc.migrations.versions.20161220124319_5891fb9375a1
* ggrc_risks.versions.20161221095515_4f82fc47b28e
* ggrc_workflows.versions.20161221095734_445ecfd7dee7
"""

from alembic import op
from sqlalchemy.sql import text


def strip_spaces_ensure_uniq(tables, field, uniq_tables):
    """Strip trailing spaces from text field and ensure uniqueness."""
    connection = op.get_bind()
    for table in tables:
        records = connection.execute(
            'SELECT {0}.id as id, {0}.{1} as value FROM {0}'.format(
                table, field))
        records = {record.id: record.value for record in records}
        uniq_values = set(records.values())
        for rec_id, rec_value in records.iteritems():
            stripped_value = rec_value if rec_value is None else rec_value.strip(
            )
            if stripped_value != rec_value:
                new_value = stripped_value
                if table in uniq_tables:
                    index = 1
                    while new_value in uniq_values:
                        new_value = '{} ({})'.format(stripped_value, index)
                        index += 1
                    uniq_values.add(new_value)
                connection.execute(
                    text('UPDATE {} SET {} = :val WHERE id = :id'.format(
                        table, field)),
                    val=new_value,
                    id=rec_id)
