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

    def fts_record_for(self, obj):
        return self.get_builder(obj.__class__).as_record(obj)

    def invalidate_cache(self):
        self.cache = defaultdict(dict)

    def search(self, terms):
        raise NotImplementedError()

    def records_generator(self, record):
        """Record generator method."""
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
        """Create records in db."""
        for db_record in self.records_generator(record):
            db.session.add(db_record)
        if commit:
            db.session.commit()

    def update_record(self, record, commit=True):
        """Update records values in db."""
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
        """Delete records values in db for specific types."""
        db.session.query(
            self.record_type).filter(self.record_type.key == key,
                                     self.record_type.type == type).delete()
        if commit:
            db.session.commit()

    def delete_records_by_ids(self, type, keys, commit=True):
        """Method to delete all records related to type and keys."""
        if not keys:
            return
        db.session.query(self.record_type).filter(
            self.record_type.key.in_(keys),
            self.record_type.type == type,
        ).delete(synchronize_session="fetch")
        if commit:
            db.session.commit()

    def delete_all_records(self, commit=True):
        """Clear index table."""
        db.session.query(self.record_type).delete()
        if commit:
            db.session.commit()

    def delete_records_by_type(self, type, commit=True):
        """Delete values from index table for selected type."""
        db.session.query(
            self.record_type).filter(self.record_type.type == type).delete()
        if commit:
            db.session.commit()
