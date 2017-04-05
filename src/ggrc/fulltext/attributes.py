# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

""" This module collect all custom full text attributes classes"""

from ggrc.utils import date_parsers

EMPTY_SUBPROPERTY_KEY = ''


class FullTextAttr(object):
  """Custom full text index attribute class

  Allowed to add full text search rule for model with custom alias,
  getting value rule and subproperties.
  Alias should be a string that will be used as search field.
  Value can be string or callable.
  If value is string, then the stored value will be the current instance
  attribute value.
  If value is callable, then the stored value will be the result of
  called value with current instance as attribute.
  Subproperties may be empty or a list of strings. Each element of the list
  should be an attribute of the stored value.
  The first subproperty in the list - the one used for sorting.
  """

  SUB_KEY_TMPL = "{id_val}-{sub}"

  def __init__(self, alias, value, subproperties=None, with_template=True):
    self.alias = alias
    self.value = value
    self.subproperties = subproperties or [EMPTY_SUBPROPERTY_KEY]
    self.with_template = with_template
    self.is_sortable = EMPTY_SUBPROPERTY_KEY not in self.subproperties

  def get_value_for(self, instance):
    """Get value from sended instance using 'value' rule"""
    if callable(self.value):
      return self.value(instance)
    return getattr(instance, self.value)

  def get_property_for(self, instance):
    """Collect property dict for sended instance"""
    value = self.get_value_for(instance)
    results = {}
    sorted_dict = {}
    sorting_subprop = self.subproperties[0]
    for subprop in self.subproperties:
      if value is not None and subprop != EMPTY_SUBPROPERTY_KEY:
        subprop_key = self.SUB_KEY_TMPL.format(id_val=value.id, sub=subprop)
        result = getattr(value, subprop)
        results[subprop_key] = result
        if result and subprop == sorting_subprop:
          sorted_dict[value.id] = unicode(result)
      else:
        results[subprop] = value
    if self.is_sortable:
      results['__sort__'] = u':'.join(sorted(sorted_dict.values()))
    return results

  @staticmethod
  def get_filter_value(value, operation):
    """Returns list of values for sent operation and value"""
    if operation in ['~', '!~']:
      return [i for i in value.split() if i]
    return [value]


class MultipleSubpropertyFullTextAttr(FullTextAttr):
  """Custom full text index attribute class for multiple return values

  subproperties required for this class
  this class required for store in full text search more than 1 returned value
  this values should be instances with `id` attribute or None values
  In the case if values is None id in subquery template will be set up as
  `EMPTY` value
  """

  def __init__(self, *args, **kwargs):
    super(MultipleSubpropertyFullTextAttr, self).__init__(*args, **kwargs)
    assert EMPTY_SUBPROPERTY_KEY not in self.subproperties
    assert self.is_sortable

  def get_property_for(self, instance):
    """Collect property for sended instance"""
    values = self.get_value_for(instance)
    results = {}
    sorted_dict = {}
    sorting_subprop = self.subproperties[0]
    for sub in self.subproperties:
      for value in values:
        if value is not None:
          sub_key = self.SUB_KEY_TMPL.format(id_val=value.id, sub=sub)
          result = getattr(value, sub)
          results[sub_key] = result
          if result and sub == sorting_subprop:
            sorted_dict[value.id] = unicode(result)
        else:
          sub_key = self.SUB_KEY_TMPL.format(id_val='EMPTY', sub=sub)
          results[sub_key] = None
    if self.is_sortable:
      results['__sort__'] = u':'.join(sorted(sorted_dict.values()))
    return results


class DatetimeValue(object):  # pylint: disable=too-few-public-methods
  """Mixin setup if expected filter value is datetime"""

  @staticmethod
  def get_filter_value(value, operation):
    """returns parsed datetime pairs for selected operation"""
    converted_pairs = date_parsers.parse_date(unicode(value))
    if not converted_pairs:
      return
    date_dict = {
        "=": converted_pairs,
        ">": (converted_pairs[1], None),
        "<": (None, converted_pairs[0]),
        ">=": (converted_pairs[0], None),
        "<=": (None, converted_pairs[1]),
    }
    return date_dict.get(operation)


class DateValue(DatetimeValue):  # pylint: disable=too-few-public-methods
  """Mixin setup if expected filter value is date"""

  def get_filter_value(self, value, operation):
    results = super(DateValue, self).get_filter_value(value, operation)
    if not results:
      return
    return [i.date() if i else i for i in results]


DatetimeFullTextAttr = type(
    "DatetimeFullTextAttr", (DatetimeValue, FullTextAttr), {})


DateFullTextAttr = type("DateFullTextAttr", (DateValue, FullTextAttr), {})


DatetimeMultipleSubpropertyFullTextAttr = type(
    "DatetimeMultipleSubpropertyFullTextAttr",
    (DatetimeValue, MultipleSubpropertyFullTextAttr),
    {},
)


DateMultipleSubpropertyFullTextAttr = type(
    "DateMultipleSubpropertyFullTextAttr",
    (DateValue, MultipleSubpropertyFullTextAttr),
    {},
)
