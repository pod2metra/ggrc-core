# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Helper to use /query api endpoint."""

import json
import operator


class WithQueryApi(object):
  """Used to construct and perform requests to /query endpoint."""

  class SORTERS(object):

    BY_ID = operator.itemgetter("id")
    BY_EMAIL = operator.itemgetter("id")

  @classmethod
  def _sort_sublists(cls, data_list, key_function=None):
    """Sort lists contained in result list.

    This function is meant to sort sublists in a list of results. Those
    sublists can only be a list of stubs from given objects. So when testing
    an order for a list, if sub elements such as related_sources, don't have
    the same order they must not raise an exception.
    """
    if key_function is None:
      key_function = cls.SORTERS.BY_ID
    for line in data_list:
      for value in line.viewvalues():
        if isinstance(value, list):
          value.sort(key=key_function)
    return data_list

  def assertEqual(self,
                  first,
                  second,
                  msg=None,
                  sort_key_function=None):
    """Assert Equality of 2 objects

    with possibility of sorting values inside"""
    if sort_key_function is not None:
      first = self._sort_sublists(first, sort_key_function)
      second = self._sort_sublists(second, sort_key_function)
    super(WithQueryApi, self).assertEqual(first, second, msg)

  def _post(self, data):
    """Make a POST to /query endpoint."""
    if not isinstance(data, list):
      data = [data]
    headers = {"Content-Type": "application/json", }
    return self.client.post("/query", data=json.dumps(data), headers=headers)

  def _get_first_result_set(self, data, *keys):
    """Post data, get response, get values from it like in obj["a"]["b"]."""
    response = self._post(data)
    self.assert200(response)
    result = json.loads(response.data)[0]
    for key in keys:
      result = result.get(key)
      self.assertIsNot(result, None)
    return result

  def _get_all_result_sets(self, data, *keys):
    """Post data, get response, get values for provided models."""
    response = self._post(data)
    self.assert200(response)
    resp_data = json.loads(response.data)

    result = []
    for obj in resp_data:
      result.extend(obj for key in keys if obj.get(key))
    return result

  @staticmethod
  def _make_query_dict_base(object_name, type_=None, filters=None,
                            limit=None, order_by=None):
    """Make a dict with query for object_name with optional parameters."""
    query = {
        "object_name": object_name,
        "filters": filters if filters else {"expression": {}},
    }
    if type_:
      query["type"] = type_
    if limit:
      query["limit"] = limit
    if order_by:
      query["order_by"] = order_by
    return query

  @staticmethod
  def make_filter_expression(expression):
    """Convert a three-tuple to a simple expression filter."""
    left, op_name, right = expression
    return {"left": left, "op": {"name": op_name}, "right": right}

  @classmethod
  def _make_query_dict(cls, object_name, expression=None, *args, **kwargs):
    """Make a dict with query for object_name with expression shortcut.

    expression should be in format: (left, op_name, right), like
    ("title", "=", "hello").
    """

    if expression:
      filters = {"expression": cls.make_filter_expression(expression)}
    else:
      filters = None

    return cls._make_query_dict_base(object_name, filters=filters, *args,
                                     **kwargs)

  @classmethod
  def _make_snapshot_query_dict(cls, child_type, expression=None, *args,
                                **kwargs):
    """Make a dict with query for Snapshots of child_type."""
    child_type_filter = cls.make_filter_expression(("child_type", "=",
                                                    child_type))
    if expression:
      snapshot_filter = cls.make_filter_expression(expression)
      filters = {"expression": {"op": {"name": "AND"},
                                "left": snapshot_filter,
                                "right": child_type_filter}}
    else:
      filters = {"expression": child_type_filter}

    return cls._make_query_dict_base("Snapshot", filters=filters, *args,
                                     **kwargs)

  def simple_query(self, model_name, expression=None, *args, **kwargs):
    return self._get_first_result_set(
        self._make_query_dict(
            model_name,
            expression=expression,
            *args,
            **kwargs
        ),
        model_name, "values"
    )
