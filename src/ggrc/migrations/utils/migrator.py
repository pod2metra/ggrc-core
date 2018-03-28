# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Migrator Utility Module.

Provides default user for migrations (migrator).  It is useful in migrations,
where user account is needed, but it is impossible to detect which user account
should be used.

It uses ``MIGRATOR`` value from the ``ggrc.settings`` module. The value should
be user's name and email in format ``User Name <email@example.com>``.

"""

from email.utils import parseaddr

# pylint: disable=invalid-name,
import sqlalchemy as sa

from ggrc import settings
from ggrc.models.person import Person


def get_migration_user_id(conn):
    """Get or create migrator account and return its ID.

  If specified migrator doesn't exists a new one will be created using values
  from ``ggrc.settings.MIGRATOR``.
  """
    meta = sa.MetaData(bind=conn)
    people = sa.Table('people', meta, autoload=True)

    name, email = parseaddr(settings.MIGRATOR)
    if not email:
        raise ValueError('Invalid migrator email. '
                         'Check MIGRATOR value within settings')
    if not name:
        name = email

    user_id = sa.select([people.c.id]).where(people.c.email == email)
    user_id = conn.execute(user_id).scalar()
    if user_id is not None:
        return user_id

    result = conn.execute(people.insert().values(  # pylint: disable=no-value-for-parameter
        email=email,
        name=name,
        created_at=sa.sql.func.now(),
        updated_at=sa.sql.func.now(),
    ))
    return result.inserted_primary_key[0]


def get_migration_user(connection):
    """Return migration user object"""
    migrator_id = get_migration_user_id(connection).id
    return Person.query.get(migrator_id)
