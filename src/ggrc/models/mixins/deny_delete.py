# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Module contains DenyDelete mixin class"""
import itertools
from collections import namedtuple

from sqlalchemy import inspect, orm

from ggrc import db

from ggrc import fulltext


class DenyDelete(object):
  """Deny delete instance if some caces happend."""

  is_delete_allowed = db.Column(db.Boolean, nullable=False, default=True)

  @classmethod
  def deny_delete(cls, ids):
    if not ids:
      return
    cls.query.filter(
        cls.id.in_(ids)
    ).update(
        {"is_delete_allowed": False},
        synchronize_session='fetch',
    )
