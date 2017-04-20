# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Module contains Indexed mixin class"""
import itertools
from collections import namedtuple

from sqlalchemy import inspect, orm

from ggrc import db

from ggrc import fulltext


ReindexRule = namedtuple("ReindexRule", ["model", "rule"])


# pylint: disable=too-few-public-methods
class Indexed(object):
  """Mixin for Index And auto reindex current model instance"""

  AUTO_REINDEX_RULES = [
      # Usage: ReindexRule("ModelName", lambda x: x.value)
  ]

  PROPERTY_TEMPLATE = u"{}"

  def delete_record(self):
    fulltext.get_indexer().delete_record(
        self.id,
        self.__class__.__name__,
        False
    )

  def create_record(self):
    indexer = fulltext.get_indexer()
    indexer.create_record(indexer.fts_record_for(self), False)

  def update_indexer(self):
    """Update indexer for current instance"""
    if self.__class__.__name__ not in fulltext.get_indexed_model_names():
      return
    self.delete_record()
    self.create_record()

  def get_reindex_pair(self):
    return (self.__class__.__name__, self.id)

  @classmethod
  def get_insert_query_for(cls, ids):
    """Return insert class record query. It will return None, if it's empty."""
    if not ids:
      return
    instances = cls.indexed_query().filter(cls.id.in_(ids))
    indexer = fulltext.get_indexer()
    keys = inspect(indexer.record_type).c
    records = (indexer.fts_record_for(i) for i in instances)
    rows = itertools.chain(*[indexer.records_generator(i) for i in records])
    values = [{c.name: getattr(r, a) for a, c in keys.items()} for r in rows]
    if values:
      return indexer.record_type.__table__.insert().values(values)

  @classmethod
  def get_delete_query_for(cls, ids):
    """Return delete class record query. If ids are empty, will return None."""
    if not ids:
      return
    indexer = fulltext.get_indexer()
    return indexer.record_type.__table__.delete().where(
        indexer.record_type.type == cls.__name__
    ).where(
        indexer.record_type.key.in_(ids)
    )

  @classmethod
  def bulk_record_update_for(cls, ids):
    """Bulky update index records for current class"""
    delete_query = cls.get_delete_query_for(ids)
    insert_query = cls.get_insert_query_for(ids)
    for query in [delete_query, insert_query]:
      if query is not None:
        db.session.execute(query)

  @classmethod
  def indexed_query(cls):
    return cls.query.options(
        orm.Load(cls).load_only("id"),
    )
