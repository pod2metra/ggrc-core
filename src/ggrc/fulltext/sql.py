# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""SQL routines for full-text indexing."""

from collections import defaultdict

from ggrc import db


class SqlIndexer(object):
  """SqlIndexer class."""

  def __init__(self, settings):
    self.indexer_rules = defaultdict(list)
    self.indexer_fields = defaultdict(set)
    self.cache = defaultdict(dict)
    self.builders = {}

  def get_builder(self, obj_class):
    """return recordbuilder for sent class

    save it in builders dict arguments and cache it here
    """
    builder = self.builders.get(obj_class.__name__)
    if builder is not None:
      return builder
    from ggrc.fulltext import recordbuilder
    builder = recordbuilder.RecordBuilder(obj_class, self)
    self.builders[obj_class.__name__] = builder
    return builder

  def invalidate_cache(self):
    self.cache = defaultdict(dict)

  def search(self, terms):
    raise NotImplementedError()

  def records_generator(self, instance):
    """Record generator method."""
    props = self.get_builder(instance.__class__).get_properties(instance)
    for prop, value in props.iteritems():
      for subproperty, content in value.iteritems():
        if content is not None:
          yield dict(
              key=instance.id,
              type=instance.type,
              context_id=instance.context_id,
              tags="",
              property=prop,
              subproperty=unicode(subproperty),
              content=unicode(content),
          )

  def create_record(self, instance, commit=True):
    """Create records in db."""
    for db_record in self.records_generator(instance):
      db.session.add(self.record_type(**db_record))
    if commit:
      db.session.commit()

  def update_record(self, instance, commit=True):
    """Update records values in db."""
    # remove the obsolete index entries
    self.delete_record(instance.id, instance.type, False)
    self.create_record(instance, commit=commit)

  def delete_record(self, key, type, commit=True):
    """Delete records values in db for specific types."""
    db.session.query(
        self.record_type
    ).filter(
        self.record_type.key == key,
        self.record_type.type == type
    ).delete(
        synchronize_session="fetch"
    )
    if commit:
      db.session.commit()

  def delete_records_by_ids(self, type, keys, commit=True):
    """Method to delete all records related to type and keys."""
    if not keys:
      return
    db.session.query(
        self.record_type
    ).filter(
        self.record_type.key.in_(keys),
        self.record_type.type == type,
    ).delete(
        synchronize_session="fetch"
    )
    if commit:
      db.session.commit()

  def delete_all_records(self, commit=True):
    """Clear index table."""
    db.session.query(self.record_type).delete()
    if commit:
      db.session.commit()

  def delete_records_by_type(self, type, commit=True):
    """Delete values from index table for selected type."""
    db.session.query(self.record_type).filter(
        self.record_type.type == type).delete()
    if commit:
      db.session.commit()
