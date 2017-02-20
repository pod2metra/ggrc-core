# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Module for full text index record builder."""

from collections import defaultdict

import flask

from ggrc import db
import ggrc.models.all_models
from ggrc.models.reflection import AttributeInfo
from ggrc.models.person import Person
from ggrc.fulltext import Record, FullTextAttr


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

    properties = {}
    for attr in self._fulltext_attrs:
      if isinstance(attr, basestring):
        properties[attr] = {"": getattr(obj, attr)}
      elif isinstance(attr, FullTextAttr):
        properties[attr.alias] = attr.get_property_for(obj)
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
    _, names, emails = zip(*(cls.get_person_id_name_email(p) for p in people))
    sort_values = (name or email for (name, email) in zip(names, emails))
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
    record_id = obj.id
    record_type = obj.__class__.__name__

    # Override defaults to index custom attribute values as attributes of the
    # parent object (the CustomAttributable).
    if record_type == "CustomAttributeValue":
      record_id = obj.attributable_id
      record_type = obj.attributable_type
      properties = self.get_custom_attribute_properties(obj)
    else:
      properties = self._get_properties(obj)

    # assignees are returned as a list:
    # [(<person1>, (role1, role2, ...)), (<person2>, (role2, ...)]
    assignees = properties.pop("assignees", None)
    if assignees:
      for assignments in assignees.values():
        role_to_people = defaultdict(list)
        for person, roles in assignments:
          if person:
            for role in roles:
              role_to_people[role].append(person)
              properties[role] = self.build_person_subprops(person)
        for role, people in role_to_people.items():
          properties[role].update(self.build_list_sort_subprop(people))

    single_person_properties = {"modified_by", "principal_assessor",
                                "secondary_assessor", "contact",
                                "secondary_contact"}

    multiple_person_properties = {"owners"}

    for prop in single_person_properties & set(properties.keys()):
      subproperties = {}
      for person in properties[prop].values():
        if person:
          subproperties.update(self.build_person_subprops(person))
          subproperties.update(self.build_list_sort_subprop([person]))
      if subproperties:
        properties[prop] = subproperties

    for prop in multiple_person_properties & set(properties.keys()):
      subproperties = {}
      for people_list in properties[prop].values():
        for person in people_list:
          subproperties.update(self.build_person_subprops(person))
        subproperties.update(self.build_list_sort_subprop(people_list))
      if subproperties:
        properties[prop] = subproperties

    return Record(
        # This logic saves custom attribute values as attributes of the object
        # that owns the attribute values. When obj is not a
        # CustomAttributeValue the values are saved directly.
        record_id,
        record_type,
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
