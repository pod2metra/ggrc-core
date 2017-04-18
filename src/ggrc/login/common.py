# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Handle the interface to GGRC models for all login methods.
"""

from ggrc import db, settings
from ggrc.models.context import Context
from ggrc.models.person import Person
from ggrc.services.common import log_event
from ggrc_basic_permissions import basic_roles
from ggrc_basic_permissions.models import UserRole


def _base_user_query():
  from sqlalchemy import orm
  return Person.query.options(
      orm.undefer_group('Person_complete'))


def find_user_by_id(user_id):
  """Find Person object by some ``id``.
  Note that ``id`` need not be Person().id, but should match the value
  returned by ``Person().get_id()``.
  """
  return _base_user_query().filter(Person.id == int(user_id)).first()


def find_user_by_email(email):
  return _base_user_query().filter(Person.email == email).first()


def add_creator_role(user):
  """Add createor role for sent user."""
  user_creator_role = UserRole(
      person=user,
      role=basic_roles.creator(),
  )
  db.session.add(user_creator_role)
  db.session.commit()
  log_event(db.session, user_creator_role, user_creator_role.id)


def create_user(email, **kwargs):
  """Create User

  attr:
      email (string) required
  """
  user = Person(email=email, **kwargs)
  db.session.add(user)
  db.session.flush()
  log_event(db.session, user, user.id)
  user_context = Context(
      name='Personal Context for {0}'.format(email),
      description='',
      related_object=user,
      context_id=1,
  )
  db.session.add(user_context)
  db.session.commit()
  return user


def find_or_create_user_by_email(email, **kwargs):
  """Generates or find user for selected email."""
  user = find_user_by_email(email)
  if not user:
    user = create_user(email, **kwargs)
    authorized_domains = getattr(settings, "AUTHORIZED_DOMAINS", set())
    # Email can have multiple @, but last one separates local and domain part
    user_domain = user.email.split("@")[-1]
    if user_domain in authorized_domains:
      add_creator_role(user)
  return user


def get_next_url(request, default_url):
  """Returns next url from requres or default url if it's not found."""
  if 'next' in request.args:
    next_url = request.args['next']
    return next_url
  else:
    return default_url
