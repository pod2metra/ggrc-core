# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""SQL routines for full-text indexing."""

from ggrc import db
from ggrc.fulltext import Indexer


class SqlIndexer(Indexer):
  def records_generator(self, record):
    for prop, value in record.properties.items():
      for subproperty, content in value.items():
        if content is not None:
          yield self.record_type(
              key=record.key,
              type=record.type,
              context_id=record.context_id,
              tags=record.tags,
              property=prop,
              subproperty=unicode(subproperty),
              content=unicode(content),
          )

  def create_record(self, record, commit=True):
    for db_record in self.records_generator(record):
      db.session.add(db_record)
    if commit:
      db.session.commit()

  def update_record(self, record, commit=True):
    # remove the obsolete index entries
    if record.properties:
      db.session.query(self.record_type).filter(
          self.record_type.key == record.key,
          self.record_type.type == record.type,
          self.record_type.property.in_(list(record.properties.keys())),
      ).delete(synchronize_session="fetch")
    # add new index entries
    self.create_record(record, commit=commit)

  def delete_record(self, key, type, commit=True):
    db.session.query(self.record_type).filter(
        self.record_type.key == key,
        self.record_type.type == type).delete()
    if commit:
      db.session.commit()

  def delete_all_records(self, commit=True):
    db.session.query(self.record_type).delete()
    if commit:
      db.session.commit()

  def delete_records_by_type(self, type, commit=True):
    db.session.query(self.record_type).filter(
        self.record_type.type == type).delete()
    if commit:
      db.session.commit()
