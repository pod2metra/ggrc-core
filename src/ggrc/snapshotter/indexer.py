# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Manage indexing for snapshotter service"""

import logging

from sqlalchemy.sql.expression import tuple_

from ggrc import db
from ggrc import models
from ggrc.models import all_models
from ggrc.fulltext.mysql import MysqlRecordProperty as Record
from ggrc.fulltext.recordbuilder import RecordBuilder
from ggrc.models.reflection import AttributeInfo
from ggrc.utils import generate_query_chunks

from ggrc.snapshotter.rules import Types
from ggrc.snapshotter.datastructures import Pair
from ggrc.fulltext.attributes import FullTextAttr


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


SINGLE_PERSON_PROPERTIES = {"modified_by", "principal_assessor",
                            "secondary_assessor", "contact",
                            "secondary_contact"}

MULTIPLE_PERSON_PROPERTIES = {"owners"}

REVISION_COLUMNS = [
    models.Revision.id,
    models.Revision.resource_type,
    models.Revision.content,
]

SNAPSHOT_COLUMNS = [
    models.Snapshot.id,
    models.Snapshot.context_id,
    models.Snapshot.parent_type,
    models.Snapshot.parent_id,
    models.Snapshot.child_type,
    models.Snapshot.child_id,
    models.Snapshot.revision_id,
]


def _get_tag(pair):
  return u"{parent_type}-{parent_id}-{child_type}".format(
      parent_type=pair.parent.type,
      parent_id=pair.parent.id,
      child_type=pair.child.type
  )


def _get_parent_property(pair):
  return u"{parent_type}-{parent_id}".format(
      parent_type=pair.parent.type,
      parent_id=pair.parent.id
  )


def _get_child_property(pair):
  return u"{child_type}-{child_id}".format(
      child_type=pair.child.type,
      child_id=pair.child.id
  )


def _get_model_properties():
  """Get indexable properties for all snapshottable objects

  Args:
    None
  Returns:
    tuple(class_properties dict, custom_attribute_definitions dict) - Tuple of
        dictionaries, first one representing a list of searchable attributes
        for every model and second one representing dictionary of custom
        attribute definition attributes.
  """
  # pylint: disable=protected-access
  class_properties = dict()
  klass_names = Types.all

  cadef_klass_names = {
      getattr(all_models, klass)._inflector.table_singular
      for klass in klass_names
  }

  cad_query = db.session.query(
      models.CustomAttributeDefinition.id,
      models.CustomAttributeDefinition.title,
  ).filter(
      models.CustomAttributeDefinition.definition_type.in_(cadef_klass_names)
  )

  for klass_name in klass_names:
    full_text_attrs = AttributeInfo.gather_attrs(
        getattr(all_models, klass_name), '_fulltext_attrs'
    )
    model_attributes = []
    for attr in full_text_attrs:
      if isinstance(attr, FullTextAttr):
        attr = attr.alias
      model_attributes.append(attr)
    class_properties[klass_name] = model_attributes

  return class_properties, cad_query.all()


def get_searchable_attributes(attributes, cad_list, content):
  """Get all searchable attributes for a given object that should be indexed

  Args:
    attributes: Attributes that should be extracted from some model
    cad_keys: IDs of custom attribute definitions
    ca_definitions: Dictionary of "CAD ID" -> "CAD title"
    content: dictionary (JSON) representation of an object
  Return:
    Dict of "key": "value" from objects revision
  """
  searchable_values = {attr: content.get(attr) for attr in attributes}

  cad_map = {cad.id: cad for cad in cad_list}

  cav_list = content.get("custom_attributes", [])

  for cav in cav_list:
    cad = cad_map.get(cav["custom_attribute_id"])
    if cad:
      searchable_values[cad.title] = cav["attribute_value"]
  return searchable_values


def _reindex(ids=None):
  """reindex snapshots for selected ids, if not ids reindex all"""
  query = db.session.query(*SNAPSHOT_COLUMNS)
  if ids:
    query = query.filter(models.Snapshot.id.in_(ids))
  for query_chunk in generate_query_chunks(query):
    reindex_snapshot_query(query_chunk)
    db.session.commit()


def reindex():
  """Reindex all snapshots."""
  _reindex()


def reindex_snapshots(snapshot_ids):
  """Reindex selected snapshots"""
  if not snapshot_ids:
    return
  _reindex(snapshot_ids)


def delete_records(snapshot_ids, commit=True):
  """Delete all records for some snapshots.
  Args:
    snapshot_ids: An iterable with snapshot IDs whose full text records should
        be deleted.
  """
  to_delete = {("Snapshot", _id) for _id in snapshot_ids}
  db.session.query(Record).filter(
      tuple_(Record.type, Record.key).in_(to_delete)
  ).delete(synchronize_session=False)
  if commit:
    db.session.commit()


def insert_records(payload, commit=True):
  """Insert records to full text table.

  Args:
    payload: List of dictionaries that represent records entries.
  """
  engine = db.engine
  engine.execute(Record.__table__.insert(), payload)
  if commit:
    db.session.commit()


def get_person_data(rec, person):
  """Get list of Person properties for fulltext indexing
  """
  subprops = RecordBuilder.build_person_subprops(person)
  data = []
  for key, val in subprops.items():
    newrec = rec.copy()
    newrec.update({"subproperty": key, "content": val})
    data += [newrec]
  return data


def get_person_sort_subprop(rec, people):
  """Get a special subproperty for sorting
  """
  subprops = RecordBuilder.build_list_sort_subprop(people)
  data = []
  for key, val in subprops.items():
    newrec = rec.copy()
    newrec.update({"subproperty": key, "content": val})
    data += [newrec]
  return data


def records_generator(properties, pair, snapshot_id, ctx_id):
  """Generates the list of records for sent property"""
  rec_tmpl = {
      "key": snapshot_id,
      "type": "Snapshot",
      "context_id": ctx_id,
      "tags": _get_tag(pair),
      "subproperty": "",
  }
  for prop, val in properties.items():
    if val is None or not prop:
      continue
    rec = rec_tmpl.copy()
    rec["property"] = prop
    rec["content"] = val
    # record stub
    if prop in SINGLE_PERSON_PROPERTIES:
      if val:
        yield get_person_data(rec, val)
        yield get_person_sort_subprop(rec, [val])
    elif prop in MULTIPLE_PERSON_PROPERTIES:
      for person in val:
        yield get_person_data(rec, person)
      yield get_person_sort_subprop(rec, val)
    elif isinstance(val, dict) and "title" in val:
      rec["content"] = val["title"]
      yield [rec]
    elif isinstance(val, (bool, int, long)):
      rec["content"] = unicode(val)
      yield [rec]
    elif isinstance(rec["content"], basestring):
      yield [rec]
    else:
      logger.warning(u"Unsupported value for %s #%s in %s %s: %r",
                     rec["type"], rec["key"], rec["property"],
                     rec["subproperty"], rec["content"])


def reindex_snapshot_query(snapshot_query):
  """Reindex for snapshot sended query"""
  # pylint: disable=too-many-locals
  snapshots = dict()
  revisions = dict()
  search_payload = list()
  snapshot_ids = set()
  object_properties, cad_list = _get_model_properties()
  for _id, ctx_id, ptype, pid, ctype, cid, revid in snapshot_query:
    pair = Pair.from_4tuple((ptype, pid, ctype, cid))
    snapshots[pair] = [_id, ctx_id, revid]
    snapshot_ids.add(_id)

  revision_query = db.session.query(*REVISION_COLUMNS).filter(
      models.Revision.id.in_({revid for _, _, revid in snapshots.values()})
  )

  for _id, _type, content in revision_query:
    revisions[_id] = get_searchable_attributes(object_properties[_type],
                                               cad_list,
                                               content)

  for pair, value in snapshots.iteritems():
    snapshot_id, ctx_id, revision_id = value
    properties = revisions[revision_id]
    properties.update({
        "parent": _get_parent_property(pair),
        "child": _get_child_property(pair),
        "child_type": pair.child.type,
        "child_id": pair.child.id
    })
    for records in records_generator(properties, pair, snapshot_id, ctx_id):
      search_payload.extend(records)

  delete_records(snapshot_ids)
  insert_records(search_payload)


def reindex_pairs(pairs):
  """Reindex selected snapshots.

  Args:
    pairs: A list of parent-child pairs that uniquely represent snapshot
    object whose properties should be reindexed.
  """

  if not pairs:
    return

  query = db.session.query(*SNAPSHOT_COLUMNS)
  pairs_filter = tuple_(
      models.Snapshot.parent_type,
      models.Snapshot.parent_id,
      models.Snapshot.child_type,
      models.Snapshot.child_id,
  ).in_({pair.to_4tuple() for pair in pairs})
  for query_chunk in generate_query_chunks(query.filter(pairs_filter)):
    reindex_snapshot_query(query_chunk)
    db.session.commit()
