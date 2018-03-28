# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Pagination helpers module for query generation."""

import sqlalchemy as sa

from ggrc import models
from ggrc import db
from ggrc.fulltext.mysql import MysqlRecordProperty as Record
from ggrc.query import custom_operators
from ggrc.query.exceptions import BadQueryException
from ggrc.utils import benchmark


def _get_limit(limit):
    """Get limit parameters for sqlalchemy."""
    try:
        first, last = [int(i) for i in limit]
    except (ValueError, TypeError):
        raise BadQueryException("Invalid limit operator. Integers expected.")

    if first < 0 or last < 0:
        raise BadQueryException("Limit cannot contain negative numbers.")
    elif first >= last:
        raise BadQueryException("Limit start should be smaller than end.")
    else:
        page_size = last - first
    return page_size, first


def apply_limit(query, limit):
    """Apply limits for pagination.

  Args:
    query: filter query;
    limit: a tuple of indexes in format (from, to); objects is sliced to
          objects[from, to].

  Returns:
    matched objects ids and total count.
  """
    page_size, first = _get_limit(limit)

    with benchmark("Apply limit: apply_limit > query_limit"):
        # Note: limit request syntax is limit:[0,10]. We are counting
        # offset from 0 as the offset of the initial row for sql is 0 (not 1).
        limit_query = query.limit(page_size).offset(first)

    return limit_query


def get_total_count(query):
    """Get count of all objects in the query."""
    with benchmark("Apply limit: apply_limit > query_count"):
        # Note: using func.count() as query.count() is generating additional
        # subquery
        # query.count() has a bug and it returns incorrect number of objects
        count_q = query.statement.with_only_columns([sa.func.count()])
        total = db.session.execute(count_q).scalar()
    return total


def _joins_and_order(counter, clause, model, tgt_class):
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

    def by_fulltext():
        """Join fulltext index table, order by indexed CA value."""
        alias = sa.orm.aliased(Record, name=u"fulltext_{}".format(counter))
        joins = [(alias,
                  sa.and_(alias.key == model.id, alias.type == model.__name__,
                          alias.property == key,
                          alias.subproperty.in_(["", "__sort__"])))]
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

    key, _ = tgt_class.attributes_map().get(key, (key, None))
    if key in custom_operators.GETATTR_WHITELIST:
        attr = getattr(model, key.encode('utf-8'), None)
        if (isinstance(attr, sa.orm.attributes.InstrumentedAttribute)
                and isinstance(attr.property,
                               sa.orm.properties.RelationshipProperty)):
            joins, order = by_foreign_key()
        else:
            # a simple attribute
            joins, order = None, attr
    else:
        # Snapshot or non object attributes are treated as custom attributes
        joins, order = by_fulltext()

    if clause.get("desc", False):
        order = order.desc()

    return joins, order


def apply_order_by(model, query, order_by, tgt_class):
    """Add ordering parameters to a query for objects.

  This works only on direct model properties and related objects defined with
  foreign keys and fails if any CAs are specified in order_by.

  Args:
    model: the model instances of which are requested in query;
    query: a query to get objects from the db;
    order_by: a list of dicts with keys "name" (the name of the field by
              which to sort) and "desc" (optional; do reverse sort if True);
    tgt_class: the snapshotted model if `model` is Snapshot else `model`.

  If sorting by a relationship field is requested, the following sorting is
  applied:
  1. If the field is a relationship to a Titled model, sort by its title.
  2. If the field is a relationship to Person, sort by its name or email (if
     name is None or empty string for a person object).
  3. Otherwise, raise a NotImplementedError.

  Returns:
    the query with sorting parameters.
  """

    join_pairs = [
        _joins_and_order(counter, clause, model, tgt_class)
        for counter, clause in enumerate(order_by)
    ]
    join_lists, orders = zip(*join_pairs)
    join_lists = [
        join_list for join_list in join_lists if join_list is not None
    ]
    for join_list in join_lists:
        query = query.outerjoin(*join_list)

    return query.order_by(*orders)
