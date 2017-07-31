# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Contains the Assignable mixin.

This allows adding various assignee types to the object, like Verifier,
Creator, etc.
"""

import sqlalchemy as sa

from ggrc import db
from ggrc.models import person
from ggrc.models import relationship
from ggrc.models import reflection


class Assignable(object):
  """Mixin for models with assignees"""

  ASSIGNEE_TYPES = set(["Assignee"])

  _api_attrs = reflection.ApiAttributes(
      reflection.Attribute("assignees", create=False, update=False),
  )

  _custom_publish = {
      "assignees": lambda obj: obj.publish_assignees(),
  }

  @property
  def assignees(self):
    """Property that returns assignees

    Returns:
        A set of assignees.
    """
    assignees_map = self._get_assignees_map()
    assignees = [
        (assignees_map[r.source_id],
         tuple(set(r.attrs["AssigneeType"].split(","))))
        for r in self.related_sources
        if "AssigneeType" in r.attrs
    ]
    assignees += [
        (assignees_map[r.destination_id],
         tuple(set(r.attrs["AssigneeType"].split(","))))
        for r in self.related_destinations
        if "AssigneeType" in r.attrs
    ]
    return assignees

  @property
  def assignees_by_type(self):
    """Property that returns assignees.

    Returns:
      a dict with keys equal to assignee types and values equal to list of
      Person objects of assignees of this type; for instance:
      {"Creator": [<Person1>, <Person2>],
       "Assessor": [<Person2>]}
    """
    assignees_map = self._get_assignees_map()

    def get_roles(rel):
      return set(rel.attrs.get("AssigneeType", "").split(","))

    result = {}
    result_inverse = {
        assignees_map[r.source_id]: get_roles(r)
        for r in self.related_sources
        if r.source_type == "Person"
    }
    result_inverse.update({
        assignees_map[r.destination_id]: get_roles(r)
        for r in self.related_destinations
        if r.destination_type == "Person"
    })

    for assignee, roles in result_inverse.items():
      for role in roles:
        result[role] = result.get(role, []) + [assignee]

    return result

  def publish_assignees(self):
    """Serialize assignees to json.

    Transforms the value of assignees_by_type property to basic structures
    (lists and dicts) that are easily represented in json.
    The people lists are sorted by names or emails.

    Returns:
      a dict with keys equal to assignee types and values equal to list of
      serialized assignees of this type; for instance:
      {"Creator": [{"id": 1, "name": "Aaron", "email": "aaron@example.com"},
                   {"id": 2, "name": None, "email": "noname@example.com"}],
       "Assessor": [{"id": 2, "name": None, "email": "noname@example.com"}]}
    """
    return {
        role: [person.log_json_base() for person in
               sorted(people, key=lambda p: (p.name or p.email).lower())]
        for role, people in self.assignees_by_type.items()
    }

  @classmethod
  def eager_query(cls):
    query = super(Assignable, cls).eager_query()
    return query.options(
        sa.orm.subqueryload("_assignees").undefer_group("Person_complete"),
    )

  @classmethod
  def indexed_query(cls):
    query = super(Assignable, cls).indexed_query()
    return query.options(
        sa.orm.subqueryload(
            "_assignees"
        ).load_only(
            "id",
            "name",
            "email",
        ),
        sa.orm.subqueryload(
            "related_sources"
        ).load_only(
            "id",
            "source_type",
            "source_id"
        ),
        sa.orm.subqueryload(
            "related_sources"
        ).joinedload(
            "relationship_attrs"
        ).load_only(
            "attr_value",
            "attr_name",
            "id",
            "relationship_id",
        ),
        sa.orm.subqueryload(
            "related_destinations"
        ).load_only(
            "id",
            "destination_type",
            "destination_id",
        ),
        sa.orm.subqueryload(
            "related_destinations"
        ).joinedload(
            "relationship_attrs"
        ).load_only(
            "attr_value",
            "attr_name",
            "id",
            "relationship_id",
        ),
    )

  @sa.ext.declarative.declared_attr
  def _assignees(self):
    """Attribute that is used to load all assigned People eagerly."""
    rel = relationship.Relationship

    assignee_id = sa.case(
        [(rel.destination_type == person.Person.__name__,
          rel.destination_id)],
        else_=rel.source_id,
    )
    assignable_id = sa.case(
        [(rel.destination_type == person.Person.__name__,
          rel.source_id)],
        else_=rel.destination_id,
    )

    return db.relationship(
        person.Person,
        primaryjoin=lambda: self.id == assignable_id,
        secondary=rel.__table__,
        secondaryjoin=lambda: person.Person.id == assignee_id,
        viewonly=True,
    )

  def _get_assignees_map(self):
    """Get a dict from Assignee id to Assignee object.

    This method uses eagerly-loaded _assignees property and does not result in
    additional DB calls.
    """
    # pylint: disable=not-an-iterable
    return {person.id: person for person in self._assignees}

  @staticmethod
  def _validate_relationship_attr(class_, source, dest, existing, name, value):
    """Validator that allows Assignable relationship attributes

    Allow relationship attribute of name "AssigneeType" with value that is a
    comma separated list of valid roles (as defined in target class).

    Args:
        class_ (class): target class of this mixin. Think of this like a class
                     method.
        source (model instance): relevant relationship source
        dest (model instance): relevant relationship destinations
        existing (dict): current attributes on the relationship
        name (string): attribute name
        value (any): attribute value. Should be string for the right attribute

    Returns:
        New attribute value (merge with existing roles) or None if the
        attribute is not valid.
    """
    if set([source.type, dest.type]) != set([class_.__name__, "Person"]):
      return None
    if name != "AssigneeType":
      return None
    new_roles = value.split(",")
    if not all(role in class_.ASSIGNEE_TYPES for role in new_roles):
      return None
    roles = set(existing.get(name, "").split(",")) | set(new_roles)
    return ",".join(role for role in roles if role)

  @classmethod
  def _get_relate_filter(cls, predicate, related_type):
    """Used for filtering by related_assignee.

    Returns:
        Boolean stating whether such an assignee exists.
    """
    # pylint: disable=invalid-name
    # The upper case variables are allowed here to shorthand the class names.
    Rel = relationship.Relationship
    RelAttr = relationship.RelationshipAttr
    Person = person.Person
    return db.session.query(Rel).join(RelAttr).join(
        Person,
        sa.or_(sa.and_(
            Rel.source_id == Person.id,
            Rel.source_type == Person.__name__
        ), sa.and_(
            Rel.destination_id == Person.id,
            Rel.destination_type == Person.__name__
        ))
    ).filter(sa.and_(
        RelAttr.attr_value.contains(related_type),
        RelAttr.attr_name == "AssigneeType",
        sa.or_(sa.and_(
            Rel.source_type == Person.__name__,
            Rel.destination_type == cls.__name__,
            Rel.destination_id == cls.id
        ), sa.and_(
            Rel.destination_type == Person.__name__,
            Rel.source_type == cls.__name__,
            Rel.source_id == cls.id
        )),
        sa.or_(predicate(Person.name), predicate(Person.email))
    )).exists()
