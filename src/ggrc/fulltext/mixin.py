# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Module contains Indexed mixin class"""
from collections import namedtuple

from sqlalchemy import orm


class ReindexRule(namedtuple("ReindexRule", ["model", "rule", "fields"])):
  """Class for keeping reindex rules"""
  __slots__ = ()

  def __new__(cls, model, rule, fields=None):
    return super(ReindexRule, cls).__new__(cls, model, rule, fields)


# pylint: disable=too-few-public-methods
class Indexed(object):
  """Mixin for Index And auto reindex current model instance"""

  AUTO_REINDEX_RULES = [
      # Usage: ReindexRule("ModelName", lambda x: x.value)
  ]
  REQUIRED_GLOBAL_REINDEX = True

  PROPERTY_TEMPLATE = u"{}"

  def get_reindex_pair(self):
    return (self.__class__.__name__, self.id)

  @classmethod
  def indexed_query(cls):
    return cls.query.options(orm.Load(cls).load_only("id"))
