# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""SQL routines for full-text indexing."""

import logging
from collections import defaultdict

from ggrc import db
from ggrc.models import all_models
from ggrc.models.reflection import AttributeInfo
from ggrc.models.person import Person
from ggrc.models.mixins import CustomAttributable
from ggrc.fulltext.attributes import FullTextAttr
from ggrc.fulltext.mixin import Indexed


LOGGER = logging.getLogger(__name__)


class SqlIndexer(object):
  """SqlIndexer class."""

  def __init__(self, settings):
    self.indexer_rules = defaultdict(list)
    self.indexer_fields = defaultdict(set)
    self.cache = defaultdict(dict)
    self._cache_ft_attrs = {}

  def get_ft_attrs(self, obj_class):
    """return recordbuilder for sent class

    save it in builders dict arguments and cache it here
    """
    if obj_class not in self._cache_ft_attrs:
      self._cache_ft_attrs[obj_class] = AttributeInfo.gather_attrs(
          obj_class,
          '_fulltext_attrs')
    return self._cache_ft_attrs[obj_class]

  def get_custom_attribute_properties(self, definition, value):
    """Get property value in case of indexing CA
    """
    # The name of the attribute property needs to be unique for each object,
    # the value comes from the custom_attribute_value
    attribute_name = definition.title
    properties = {}
    if value and definition.attribute_type == "Map:Person":
      properties[attribute_name] = self.build_person_subprops(value)
      properties[attribute_name].update(self.build_list_sort_subprop([value]))
    else:
      properties[attribute_name] = {"": definition.get_indexed_value(value)}
    return properties

  def get_properties(self, obj):
    """Get indexable properties and values.

    Properties should be returned in the following format:
    {
      property1: {
        subproperty1: value1,
        subproperty2: value2,
        ...
      },
      ...
    }
    If there is no subproperty - empty string is used as a key
    """
    if obj.type == "Snapshot":
      # Snapshots do not have any indexable content. The object content for
      # snapshots is stored in the revision. Snapshots can also be made for
      # different models so we have to get fulltext attrs for the actual child
      # that was snapshotted and get data for those from the revision content.
      tgt_class = getattr(all_models, obj.child_type, None)
      if not tgt_class:
        return {}
      attrs = self.get_ft_attrs(tgt_class)
      return {attr: {"": obj.revision.content.get(attr)} for attr in attrs}

    if isinstance(obj, Indexed):
      property_tmpl = obj.PROPERTY_TEMPLATE
    else:
      property_tmpl = u"{}"

    properties = {}

    for attr in self.get_ft_attrs(obj.__class__):
      if isinstance(attr, basestring):
        properties[property_tmpl.format(attr)] = {"": getattr(obj, attr)}
      elif isinstance(attr, FullTextAttr):
        properties.update(attr.get_property_for(obj))

    if isinstance(obj, CustomAttributable):
      cavs = {v.custom_attribute_id: v for v in obj.custom_attribute_values}
      for cad in obj.custom_attribute_definitions:
        cav = cavs.get(cad.id)
        if not cav:
          value = cad.default_value
        elif cad.attribute_type == "Map:Person":
          value = cav.attribute_object if cav.attribute_object_id else None
        else:
          value = cav.attribute_value
        properties.update(self.get_custom_attribute_properties(cad, value))
    return properties

  def get_person_id_name_email(self, person):
    """Get id, name and email for person (either object or dict).

    If there is a global people map, get the data from it instead of the DB.
    """
    if isinstance(person, dict):
      person_id = person["id"]
    else:
      person_id = person.id
    if person_id in self.cache['people_map']:
      person_name, person_email = self.cache['people_map'][person_id]
    else:
      if isinstance(person, dict):
        person = db.session.query(Person).filter_by(
          id=person["id"]
        ).one()
      person_id = person.id
      person_name = person.name
      person_email = person.email
      self.cache['people_map'][person_id] = (person_name, person_email)
    return person_id, person_name, person_email

  def get_ac_role_person_id(self, ac_list):
    """Get ac_role name and person name for ac_role (either object or dict).

    If there is a global ac_role map, get the data from it instead of the DB.
    """
    if isinstance(ac_list, dict):
      ac_role_id = ac_list["ac_role_id"]
      ac_person_id = ac_list["person_id"]
    else:
      ac_role_id = ac_list.ac_role_id
      ac_person_id = ac_list.person_id
    if ac_role_id not in self.cache['ac_role_map']:
      ac_role = db.session.query(all_models.AccessControlRole).get(ac_role_id)
      # Internal roles should not be indexed
      if ac_role and ac_role.internal:
        self.cache['ac_role_map'][ac_role_id] = None
      else:
        ac_role_name = ac_role.name if ac_role else None
        self.cache['ac_role_map'][ac_role_id] = ac_role_name
        if ac_role_name is None:
          # index only existed role, if it have already been
          # removed than nothing to index.
          LOGGER.error(
            "Trying to index not existing ACR with id %s", ac_role_id
          )
    ac_role_name = self.cache['ac_role_map'][ac_role_id]
    if ac_role_name:
      ac_role_name = ac_role_name.lower()
    return ac_role_name, ac_person_id

  def build_person_subprops(self, person):
    """Get dict of Person properties for fulltext indexing

    If Person provided by Revision, need to go to DB to get Person data
    """
    subproperties = {}
    person_id, person_name, person_email = self.get_person_id_name_email(
      person
    )
    subproperties["{}-email".format(person_id)] = person_email
    subproperties["{}-name".format(person_id)] = person_name
    return subproperties

  def build_list_sort_subprop(self, people):
    """Get a special subproperty for sorting.

    Its content is :-separated sorted list of (name or email) of the people in
    list.
    """
    if not people:
      return {"__sort__": ""}
    _, _, emails = zip(*(self.get_person_id_name_email(p) for p in people))
    content = ":".join(sorted(emails))
    return {"__sort__": content}

  def invalidate_cache(self):
    self.cache = defaultdict(dict)

  def search(self, terms):
    raise NotImplementedError()

  def records_generator(self, obj):
    """Record generator method."""
    for prop, value in self.get_properties(obj).iteritems():
      for subproperty, content in value.items():
        if content is not None:
          yield self.record_type(
              key=obj.id,
              type=obj.type,
              context_id=obj.context_id,
              tags="",
              property=prop,
              subproperty=unicode(subproperty),
              content=unicode(content),
          )

  def create_record(self, obj, commit=True):
    """Create records in db."""
    for record in self.records_generator(obj):
      db.session.add(record)
    if commit:
      db.session.commit()

  def update_record(self, instance, commit=True):
    """Update records values in db."""
    # remove the obsolete index entries
    self.delete_record(instance, False)
    self.create_record(instance, commit)

  def delete_record(self, instance, commit=True):
    """Delete records values in db for specific types."""
    db.session.query(self.record_type).filter(
        self.record_type.key == instance.id,
        self.record_type.type == instance.type,
    ).delete()
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
