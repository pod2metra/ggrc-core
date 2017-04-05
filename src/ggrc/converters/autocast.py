# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Autocast module, populate sent expression"""

import sqlalchemy as sa

from ggrc import db
from ggrc.models.custom_attribute_definition import CustomAttributeDefinition
from ggrc.models.reflection import AttributeInfo
from ggrc.fulltext.mixin import Indexed
from ggrc.fulltext.attributes import FullTextAttr, DatetimeValue, DateValue


EXP_TMPL = {'is_autocasted': True}


NOT_AUTOCASTED_OPERATIONS = ["AND",
                             "OR",
                             "is",
                             "similar",
                             "owned",
                             "relevant",
                             "related_people",
                             "text_search"]


def build_exp(left, right, operation):
  """Util function, Build exp for left and right if they are not empty"""
  if not left or not right:
    return None
  tmp_exp = EXP_TMPL.copy()
  tmp_exp.update({
      "left": left,
      "right": right,
      "op": {"name": operation}
  })
  return tmp_exp


def is_autocast_required_for(exp):
  """Check if autocast is really needed"""
  operation = exp["op"]["name"]
  return not (
      not isinstance(operation, basestring) or
      exp.get("is_autocasted") or
      operation in NOT_AUTOCASTED_OPERATIONS
  )


def get_fulltext_parsed_value(klass, key):
  """Get fulltext parser if it's exists """
  attrs = AttributeInfo.gather_attrs(klass, '_fulltext_attrs')
  if not issubclass(klass, Indexed):
    return
  for attr in attrs:
    if isinstance(attr, FullTextAttr) and attr.with_template:
      attr_key = klass.PROPERTY_TEMPLATE.format(attr.alias)
    elif isinstance(attr, FullTextAttr):
      attr_key = attr.alias
    else:
      attr_key = klass.PROPERTY_TEMPLATE.format(attr)
      attr = FullTextAttr(key, key)
    if attr_key == key:
      return attr


def get_parsers(klass, key):
  """Return tuple of 2 parsers related to current key and class"""
  fulltext_parser = get_fulltext_parsed_value(klass, key)
  if fulltext_parser:
    if isinstance(fulltext_parser, DatetimeValue):
      return (fulltext_parser, None)
    else:
      return (None, fulltext_parser)
  try:
    attr_type = getattr(klass, key).property.columns[0].type
  except AttributeError:
    value_types = [i[0] for i in db.session.query(
        CustomAttributeDefinition.attribute_type
    ).filter(
        CustomAttributeDefinition.title == key,
        CustomAttributeDefinition.definition_type ==
        klass._inflector.table_singular  # pylint: disable=protected-access
    ).distinct()]
    is_date = CustomAttributeDefinition.ValidTypes.DATE in value_types
    is_any_value = len(value_types) > int(is_date)
    return (DateValue() if is_date else None,
            FullTextAttr(key, key) if is_any_value else None)
  if isinstance(attr_type, sa.sql.sqltypes.DateTime):
    return (DatetimeValue(), None)
  elif isinstance(attr_type, sa.sql.sqltypes.Date):
    return (DateValue(), None)
  return (None, FullTextAttr(key, key))


def autocast(exp, target_class):
  """Try to guess the type of `value` and parse it from the string.

  Args:
    operator_name: the name of the operator being applied.
    value: the value being compared.
  """
  if not is_autocast_required_for(exp):
    return exp
  operation = exp["op"]["name"]
  exp.update(EXP_TMPL)
  key = exp['left']
  key = key.lower()
  key, _ = target_class.attributes_map().get(key, (key, None))
  extra_parser, any_parser = get_parsers(target_class, key)
  if not extra_parser and not any_parser:
    # It's look like filter by snapshot
    return exp
  extra_exp = None
  current_exp = None
  if extra_parser:
    left_date, right_date = extra_parser.get_filter_value(
        unicode(exp['right']), operation) or [None, None]
    left_exp = build_exp(key,
                         left_date,
                         ">=" if operation == "=" else operation)
    right_exp = build_exp(key,
                          right_date,
                          "<=" if operation == "=" else operation)
    extra_exp = build_exp(left_exp, right_exp, "AND") or left_exp or right_exp
  if any_parser:
    for value in any_parser.get_filter_value(unicode(exp['right']), operation):
      tmp_exp = build_exp(key, value, operation)
      current_exp = build_exp(
          current_exp, tmp_exp, 'OR' if operation == "~" else "AND"
      ) or tmp_exp
  return build_exp(extra_exp, current_exp, "OR") or current_exp or extra_exp
