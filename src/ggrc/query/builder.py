# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Default query builder for /query API.

This class is used to build SqlAlchemy queries and fetch the result ids.
"""

# flake8: noqa
import collections
import datetime

import flask
import sqlalchemy as sa

from ggrc import db
from ggrc import models
from ggrc.fulltext.mysql import MysqlRecordProperty as Record
from ggrc.models import inflector
from ggrc.rbac import context_query_filter
from ggrc.utils import benchmark
from ggrc.rbac import permissions
from ggrc.query import custom_operators
from ggrc.query.exceptions import BadQueryException


# pylint: disable=too-few-public-methods

class QueryHelper(object):

  """Helper class for handling request queries

  Primary use for this class is to get list of object ids for each object type
  defined in the query. All objects must pass the query filters if they are
  defined.

  query object = [
    {
      object_name: search class name,
      permissions: either read or update, if none are given it defaults to read
      order_by: [
        {
          "name": the name of the field by which to do the sorting
          "desc": optional; if True, invert the sorting order
        }
      ]
      limit: [from, to] - limit the result list to a slice result[from, to]
      filters: {
        relevant_filters:
          these filters will return all ids of the "search class name" object
          that are mapped to objects defined in the dictionary inside the list.
          [ list of filters joined by OR expression
            [ list of filters joined by AND expression
              {
                "object_name": class of relevant object,
                "slugs": list of relevant object slugs,
                        optional and if exists will be converted into ids
                "ids": list of relevant object ids
              }
            ]
          ],
        object_filters: {
          TODO: allow filtering by title, description and other object fields
        }
      }
    }
  ]

  After the query is done (by `get_ids` method), the results are appended to
  each query object:

  query object with results = [
    {
      object_name: search class name,
      (all other object query fields)
      ids: [ list of filtered objects ids ]
    }
  ]

  The result fields may or may not be present in the resulting query depending
  on the attributes of `get` method.

  """

  def __init__(self, query):
    self.query = self._clean_query(query)
    self._count = 0

  def _get_snapshot_child_type(self, object_query):
    """Return child_type for snapshot from a query"""
    return self._find_child_type(
        object_query.get("filters", {}).get("expression"), ""
    )

  def _find_child_type(self, expr, child_type):
    """Search for child_type recursively down the query expression."""
    if child_type:
      return child_type
    left, oper, right = expr.get("left"), expr.get("op", {}), expr.get("right")
    if oper.get("name") == "=":
      if left == "child_type" and isinstance(right, basestring):
        child_type = right
    else:
      for node in (left, right):
        if isinstance(node, dict):
          child_type = self._find_child_type(node, child_type)
    return child_type

  def _clean_query(self, query):
    """ sanitize the query object """
    for object_query in query:
      if "object_name" not in object_query:
        raise BadQueryException("`object_name` required for each object block")
      filters = object_query.get("filters", {}).get("expression")
      self._clean_filters(filters)
      self._macro_expand_object_query(object_query)
    return query

  def _clean_filters(self, expression):
    """Prepare the filter expression for building the query."""
    if not expression or not isinstance(expression, dict):
      return
    slugs = expression.get("slugs")
    if slugs:
      ids = expression.get("ids", [])
      ids.extend(self._slugs_to_ids(expression["object_name"], slugs))
      expression["ids"] = ids
    try:
      expression["ids"] = [int(id_) for id_ in expression.get("ids", [])]
    except ValueError as error:
      # catch missing relevant filter (undefined id)
      if expression.get("op", {}).get("name", "") == "relevant":
        raise BadQueryException(u"Invalid relevant filter for {}".format(
                                expression.get("object_name", "")))
      raise error
    self._clean_filters(expression.get("left"))
    self._clean_filters(expression.get("right"))

  def _expression_keys(self, exp):
    """Return the list of keys specified in the expression."""
    operator_name = exp.get("op", {}).get("name", None)
    if operator_name in ["AND", "OR"]:
      return self._expression_keys(exp["left"]).union(
          self._expression_keys(exp["right"]))
    left = exp.get("left", None)
    if left is not None and isinstance(left, collections.Hashable):
      return set([left])
    else:
      return set()

  def _macro_expand_object_query(self, object_query):
    """Expand object query."""
    def expand_task_dates(exp):
      """Parse task dates from the specified expression."""
      if not isinstance(exp, dict) or "op" not in exp:
        return
      operator_name = exp["op"]["name"]
      if operator_name in ["AND", "OR"]:
        expand_task_dates(exp["left"])
        expand_task_dates(exp["right"])
      elif isinstance(exp["left"], (str, unicode)):
        key = exp["left"]
        if key in ["start", "end"]:
          parts = exp["right"].split("/")
          if len(parts) == 3:
            try:
              month, day, year = [int(part) for part in parts]
            except Exception:
              raise BadQueryException(
                  "Date must consist of numbers")
            exp["left"] = key + "_date"
            exp["right"] = datetime.date(year, month, day)
          elif len(parts) == 2:
            month, day = parts
            exp["op"] = {"name": u"AND"}
            exp["left"] = {
                "op": {"name": operator_name},
                "left": "relative_" + key + "_month",
                "right": month,
            }
            exp["right"] = {
                "op": {"name": operator_name},
                "left": "relative_" + key + "_day",
                "right": day,
            }
          elif len(parts) == 1:
            exp["left"] = "relative_" + key + "_day"
          else:
            raise BadQueryException(u"Field {} should be a date of one of the"
                                    u" following forms: DD, MM/DD, MM/DD/YYYY"
                                    .format(key))

    if object_query["object_name"] == "TaskGroupTask":
      filters = object_query.get("filters")
      if filters is not None:
        exp = filters["expression"]
        keys = self._expression_keys(exp)
        if "start" in keys or "end" in keys:
          expand_task_dates(exp)

  def get_ids(self):
    """Get a list of filtered object IDs.

    self.query should contain a list of queries for different objects which
    will get evaluated and turned into a list of object IDs.

    Returns:
      list of dicts: same query as the input with all ids that match the filter
    """
    for object_query in self.query:
      ids = self._get_ids(object_query)
      object_query["ids"] = ids
    return self.query

  @staticmethod
  def _get_type_query(model, permission_type):
    """Filter by contexts and resources

    Prepare query to filter models based on the available contexts and
    resources for the given type of object.
    """
    contexts, resources = permissions.get_context_resource(
        model_name=model.__name__, permission_type=permission_type
    )

    if contexts is not None:
      if resources:
        resource_sql = model.id.in_(resources)
      else:
        resource_sql = sa.sql.false()

      return sa.or_(
          context_query_filter(model.context_id, contexts),
          resource_sql)

  def _get_objects(self, object_query):
    """Get a set of objects described in the filters."""

    with benchmark("Get ids: _get_objects -> _get_ids"):
      ids = self._get_ids(object_query)
    if not ids:
      return set()

    object_name = object_query["object_name"]
    object_class = inflector.get_model(object_name)
    query = object_class.eager_query()
    query = query.filter(object_class.id.in_(ids))

    with benchmark("Get objects by ids: _get_objects -> obj in query"):
      id_object_map = {obj.id: obj for obj in query}

    with benchmark("Order objects by ids: _get_objects"):
      objects = [id_object_map[id_] for id_ in ids]

    return objects

  def _get_ids(self, object_query):
    """Get a set of ids of objects described in the filters."""

    object_name = object_query["object_name"]
    expression = object_query.get("filters", {}).get("expression")

    if expression is None:
      return set()
    object_class = inflector.get_model(object_name)
    query = db.session.query(object_class.id)

    tgt_class = object_class
    if object_name == "Snapshot":
      child_type = self._get_snapshot_child_type(object_query)
      tgt_class = getattr(models.all_models, child_type, object_class)

    requested_permissions = object_query.get("permissions", "read")
    with benchmark("Get permissions: _get_ids > _get_type_query"):
      type_query = self._get_type_query(object_class, requested_permissions)
      if type_query is not None:
        query = query.filter(type_query)
    with benchmark("Parse filter query: _get_ids > _build_expression"):
      filter_expression = custom_operators.build_expression(
          expression,
          object_class,
          tgt_class,
          self.query
      )
      if filter_expression is not None:
        query = query.filter(filter_expression)
    if object_query.get("order_by"):
      with benchmark("Sorting: _get_ids > order_by"):
        query = self._apply_order_by(
            object_class,
            query,
            object_query["order_by"],
            tgt_class,
        )
    with benchmark("Apply limit"):
      limit = object_query.get("limit")
      if limit:
        ids, total = self._apply_limit(query, limit)
      else:
        ids = [obj.id for obj in query]
        total = len(ids)
      object_query["total"] = total

    if hasattr(flask.g, "similar_objects_query"):
      # delete similar_objects_query for the case when several queries are
      # POSTed in one request, the first one filters by similarity and the
      # second one doesn't but tries to sort by __similarity__
      delattr(flask.g, "similar_objects_query")
    return ids

  @staticmethod
  def _apply_limit(query, limit):
    """Apply limits for pagination.

    Args:
      query: filter query;
      limit: a tuple of indexes in format (from, to); objects is sliced to
            objects[from, to].

    Returns:
      matched objects ids and total count.
    """
    try:
      first, last = limit
      first, last = int(first), int(last)
    except (ValueError, TypeError):
      raise BadQueryException("Invalid limit operator. Integers expected.")

    if first < 0 or last < 0:
      raise BadQueryException("Limit cannot contain negative numbers.")
    elif first >= last:
      raise BadQueryException("Limit start should be smaller than end.")
    else:
      page_size = last - first
      with benchmark("Apply limit: _apply_limit > query_limit"):
        # Note: limit request syntax is limit:[0,10]. We are counting
        # offset from 0 as the offset of the initial row for sql is 0 (not 1).
        ids = [obj.id for obj in query.limit(page_size).offset(first)]
      with benchmark("Apply limit: _apply_limit > query_count"):
        if len(ids) < page_size:
          total = len(ids) + first
        else:
          # Note: using func.count() as query.count() is generating additional
          # subquery
          count_q = query.statement.with_only_columns([sa.func.count()])
          total = db.session.execute(count_q).scalar()

    return ids, total

  def _apply_order_by(self, model, query, order_by, tgt_class):
    """Add ordering parameters to a query for objects.

    This works only on direct model properties and related objects defined with
    foreign keys and fails if any CAs are specified in order_by.

    Args:
      model: the model instances of which are requested in query;
      query: a query to get objects from the db;
      order_by: a list of dicts with keys "name" (the name of the field by which
                to sort) and "desc" (optional; do reverse sort if True);
      tgt_class: the snapshotted model if `model` is Snapshot else `model`.

    If order_by["name"] == "__similarity__" (a special non-field value),
    similarity weights returned by get_similar_objects_query are used for
    sorting.

    If sorting by a relationship field is requested, the following sorting is
    applied:
    1. If the field is a relationship to a Titled model, sort by its title.
    2. If the field is a relationship to Person, sort by its name or email (if
       name is None or empty string for a person object).
    3. Otherwise, raise a NotImplementedError.

    Returns:
      the query with sorting parameters.
    """
    def joins_and_order(clause):
      """Get join operations and ordering field from item of order_by list.

      Args:
        clause: {"name": the name of model's field,
                 "desc": reverse sort on this field if True}

      Returns:
        ([joins], order) - a tuple of joins required for this ordering to work
                           and ordering clause itself; join is None if no join
                           required or [(aliased entity, relationship field)]
                           if joins required.
      """
      def by_similarity():
        """Join similar_objects subquery, order by weight from it."""
        join_target = flask.g.similar_objects_query.subquery()
        join_condition = model.id == join_target.c.id
        joins = [(join_target, join_condition)]
        order = join_target.c.weight
        return joins, order

      def by_fulltext():
        """Join fulltext index table, order by indexed CA value."""
        alias = sa.orm.aliased(Record, name=u"fulltext_{}".format(self._count))
        joins = [(alias, sa.and_(
            alias.key == model.id,
            alias.type == model.__name__,
            alias.property == key,
            alias.subproperty.in_(["", "__sort__"]))
        )]
        order = alias.content
        return joins, order

      def by_foreign_key():
        """Join the related model, order by title or name/email."""
        related_model = attr.property.mapper.class_
        if issubclass(related_model, models.mixins.Titled):
          joins = [(alias, _)] = [(sa.orm.aliased(attr), attr)]
          order = alias.title
        else:
          raise NotImplementedError(u"Sorting by {model.__name__} is "
                                    u"not implemented yet."
                                    .format(model=related_model))
        return joins, order

      # transform clause["name"] into a model's field name
      key = clause["name"].lower()

      if key == "__similarity__":
        # special case
        if hasattr(flask.g, "similar_objects_query"):
          joins, order = by_similarity()
        else:
          raise BadQueryException("Can't order by '__similarity__' when no "
                                  "'similar' filter was applied.")
      else:
        key, _ = tgt_class.attributes_map().get(key, (key, None))
        if key in custom_operators.GETATTR_WHITELIST:
          attr = getattr(model, key.encode('utf-8'), None)
          if (isinstance(attr, sa.orm.attributes.InstrumentedAttribute) and
              isinstance(attr.property,
                         sa.orm.properties.RelationshipProperty)):
            joins, order = by_foreign_key()
          else:
            # a simple attribute
            joins, order = None, attr
        else:
          # Snapshot or non object attributes are treated as custom attributes
          self._count += 1
          joins, order = by_fulltext()

      if clause.get("desc", False):
        order = order.desc()

      return joins, order

    join_lists, orders = zip(*[joins_and_order(clause) for clause in order_by])
    for join_list in join_lists:
      if join_list is not None:
        for join in join_list:
          query = query.outerjoin(*join)

    return query.order_by(*orders)

  @staticmethod
  def _slugs_to_ids(object_name, slugs):
    """Convert SLUG to proper ids for the given objec."""
    object_class = inflector.get_model(object_name)
    if not object_class:
      return []
    ids = [c.id for c in object_class.query.filter(
        object_class.slug.in_(slugs)).all()]
    return ids
