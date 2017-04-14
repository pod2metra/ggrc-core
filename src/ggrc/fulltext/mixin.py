# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Module contains Indexed mixin class"""
import itertools
from collections import namedtuple

from sqlalchemy import inspect

from ggrc import db

from . import get_indexer, get_indexed_model_names


ReindexRule = namedtuple("ReindexRule", ["model", "rule"])


# pylint: disable=too-few-public-methods
class Indexed(object):
  """Mixin for Index And auto reindex current model instance"""

  AUTO_REINDEX_RULES = [
      # Usage: ReindexRule("ModelName", lambda x: x.value)
  ]

  PROPERTY_TEMPLATE = u"{}"

  def delete_record(self):
    get_indexer().delete_record(self.id, self.__class__.__name__, False)

  def create_record(self):
    indexer = get_indexer()
    indexer.create_record(indexer.fts_record_for(self), False)

  def update_indexer(self):
    """Update indexer for current instance"""
    if self.__class__.__name__ not in get_indexed_model_names():
      return
    self.delete_record()
    self.create_record()

  def get_reindex_pair(self):
    return (self.__class__.__name__, self.id)

  @classmethod
  def bulk_record_update_for(cls, ids):
    """Bulky update index records for current class"""
    if not ids:
      return
    db.session.execute("SET unique_checks=0;")
    db.session.execute("SET foreign_key_checks=0;")
    records = []
    indexer = get_indexer()
    record_model = indexer.record_type
    for instance in cls.indexed_query().filter(cls.id.in_(ids)).all():
      records.append(indexer.fts_record_for(instance))
    db.session.execute(record_model.__table__.delete().where(
        record_model.type == cls.__name__
    ).where(
        record_model.key.in_(ids)
    ))
    db_records = itertools.chain(
        *[indexer.records_generator(i) for i in records]
    )
    keys = inspect(record_model).c
    values = [{c.name: getattr(db_record, a) for a, c in keys.items()}
              for db_record in db_records]
    if not values:
      return
    db.session.execute(record_model.__table__.insert().values(values))
    db.session.execute("SET unique_checks=1;")
    db.session.execute("SET foreign_key_checks=1;")

  @classmethod
  def indexed_query(cls):
    return cls.query
