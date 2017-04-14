# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Module for full text index record builder."""

import flask

from ggrc import db
import ggrc.models.all_models
from ggrc.models.reflection import AttributeInfo
from ggrc.models.person import Person
from ggrc.models.mixins import CustomAttributable
from ggrc.fulltext import Record
from ggrc.fulltext.attributes import FullTextAttr
from ggrc.fulltext.mixin import Indexed


class RecordBuilder(object):
  """Basic record builder for full text index table."""
  # pylint: disable=too-few-public-methods

  def __init__(self, tgt_class):
    self._fulltext_attrs = AttributeInfo.gather_attrs(
        tgt_class, '_fulltext_attrs')

  def _get_properties(self, obj):
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
      tgt_class = getattr(ggrc.models.all_models, obj.child_type, None)
      if not tgt_class:
        return {}
      attrs = AttributeInfo.gather_attrs(tgt_class, '_fulltext_attrs')
      return {attr: {"": obj.revision.content.get(attr)} for attr in attrs}

    if isinstance(obj, Indexed):
      property_tmpl = obj.PROPERTY_TEMPLATE
    else:
      property_tmpl = u"{}"

    properties = {}
    for attr in self._fulltext_attrs:
      if isinstance(attr, basestring):
        properties[property_tmpl.format(attr)] = {"": getattr(obj, attr)}
      elif isinstance(attr, FullTextAttr):
        if attr.with_template:
          property_name = property_tmpl.format(attr.alias)
        else:
          property_name = attr.alias
        properties[property_name] = attr.get_property_for(obj)
    return properties

  @staticmethod
  def get_person_id_name_email(person):
    """Get id, name and email for person (either object or dict).

    If there is a global people map, get the data from it instead of the DB.
    """
    if hasattr(flask.g, "people_map"):
      if isinstance(person, dict):
        person_id = person["id"]
      else:
        person_id = person.id
      person_name, person_email = flask.g.people_map[person_id]
    else:
      if isinstance(person, dict):
        person = db.session.query(Person).filter_by(id=person["id"]).one()
      person_id = person.id
      person_name = person.name
      person_email = person.email
    return person_id, person_name, person_email

  @classmethod
  def build_person_subprops(cls, person):
    """Get dict of Person properties for fulltext indexing

    If Person provided by Revision, need to go to DB to get Person data
    """
    subproperties = {}
    person_id, person_name, person_email = cls.get_person_id_name_email(person)
    subproperties["{}-name".format(person_id)] = person_name
    subproperties["{}-email".format(person_id)] = person_email
    return subproperties

  @classmethod
  def build_list_sort_subprop(cls, people):
    """Get a special subproperty for sorting.

    Its content is :-separated sorted list of (name or email) of the people in
    list.
    """
    if not people:
      return {"__sort__": ""}
    _, _, emails = zip(*(cls.get_person_id_name_email(p) for p in people))
    sort_values = (email.split("@")[0] for email in emails)
    content = ":".join(sorted(sort_values))
    return {"__sort__": content}

  def get_custom_attribute_properties(self, obj):
    """Get property value in case of indexing CA
    """
    # The name of the attribute property needs to be unique for each object,
    # the value comes from the custom_attribute_value
    attribute_name = obj.custom_attribute.title
    properties = {}
    if (obj.custom_attribute.attribute_type == "Map:Person" and
            obj.attribute_object_id):
      properties[attribute_name] = self.build_person_subprops(
          obj.attribute_object)
      properties[attribute_name].update(self.build_list_sort_subprop(
          [obj.attribute_object]))
    else:
      properties[attribute_name] = {"": obj.attribute_value}
    return properties

  def as_record(self, obj):  # noqa  # pylint:disable=too-many-branches
    """Generate record representation for an object.

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
    # Defaults. These work when the record is not a custom attribute

    properties = self._get_properties(obj)
    if isinstance(obj, CustomAttributable):
      for custom_attr in obj.custom_attribute_values:
        properties.update(self.get_custom_attribute_properties(custom_attr))

    return Record(
        # This logic saves custom attribute values as attributes of the object
        # that owns the attribute values. When obj is not a
        # CustomAttributeValue the values are saved directly.
        obj.id,
        obj.__class__.__name__,
        obj.context_id,
        properties
    )


def get_record_builder(obj, builders={}):
  # pylint: disable=dangerous-default-value
  # This default value is used for simple memoization and should be refactored
  # with proper memoization in the future.
  """Get a record builder for a given class."""
  builder = builders.get(obj.__class__.__name__)
  if builder is None:
    builder = RecordBuilder(obj.__class__)
    builders[obj.__class__.__name__] = builder
  return builder


def fts_record_for(obj):
  builder = get_record_builder(obj)
  return builder.as_record(obj)
