# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Module contains Indexed mixin class"""
import itertools
from collections import namedtuple

from sqlalchemy import orm

from ggrc import db

from ggrc import fulltext
from ggrc import utils


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

  INDEX_CHUNK_SIZE = 1000

  def get_reindex_pair(self):
    return (self.__class__.__name__, self.id)

  @classmethod
  def insert_queries_generator(cls, ids):
    """Return insert class record query. It will return None, if it's empty."""
    indexer = fulltext.get_indexer()
    if ids:
      instances = cls.indexed_query().filter(cls.id.in_(ids))
      rows = itertools.chain(*[
          indexer.records_generator(i) for i in instances
      ])
      for values in utils.chunks_generator(rows, cls.INDEX_CHUNK_SIZE):
        yield indexer.record_type.__table__.insert().values(values)

  @classmethod
  def delete_queries_generator(cls, ids):
    """Return delete class record query. If ids are empty, will return None."""
    indexer = fulltext.get_indexer()
    for ids_chunk in utils.chunks_generator(ids or [], cls.INDEX_CHUNK_SIZE):
      yield indexer.record_type.__table__.delete().where(
          indexer.record_type.type == cls.__name__
      ).where(
          indexer.record_type.key.in_(ids_chunk)
      )

  @classmethod
  def bulk_record_update_for(cls, ids):
    """Bulky update index records for current class"""
    for query in itertools.chain(*[cls.delete_queries_generator(ids),
                                   cls.insert_queries_generator(ids)]):
      db.session.execute(query)

  @classmethod
  def indexed_query(cls):
    return cls.query.options(
        orm.Load(cls).load_only("id"),
    )
