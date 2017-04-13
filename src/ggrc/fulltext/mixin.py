# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Module contains Indexed mixin class"""

from collections import namedtuple
from . import get_indexed_model_names, get_indexer


ReindexRule = namedtuple("ReindexRule", ["model", "rule"])


# pylint: disable=too-few-public-methods
class Indexed(object):
  """Mixin for Index And auto reindex current model instance"""

  AUTO_REINDEX_RULES = [
      # Usage: ReindexRule("ModelName", lambda x: x.value)
  ]

  PROPERTY_TEMPLATE = u"{}"

  def delere_record(self):
    get_indexer().delete_record(self.id, self.__class__.__name__, False)

  def create_record(self):
    from .recordbuilder import fts_record_for
    get_indexer().create_record(fts_record_for(self), False)

  def update_indexer(self):
    """Update indexer for current instance"""
    if self.__class__.__name__ not in get_indexed_model_names():
      return
    self.delere_record()
    self.create_record()

  @classmethod
  def indexed_query(cls):
    return cls.query
