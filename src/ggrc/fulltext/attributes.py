# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

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
  Subproperties may be empty or the list of strings. Each element of that list
  Should be an attribute of the stored value.
  """

  SUB_KEY_TMPL = "{id_val}-{sub}"

  def __init__(self, alias, value, subproperties=None, with_template=True):
    self.alias = alias
    self.value = value
    self.subproperties = subproperties or [EMPTY_SUBPROPERTY_KEY]
    self.with_template = with_template

  def get_value_for(self, instance):
    """Get value from sended instance using 'value' rule"""
    if callable(self.value):
      return self.value(instance)
    return getattr(instance, self.value)

  def get_property_for(self, instance):
    """Collect property dict for sended instance"""
    value = self.get_value_for(instance)
    results = {}
    for subprop in self.subproperties:
      if value is not None and subprop != EMPTY_SUBPROPERTY_KEY:
        subprop_key = self.SUB_KEY_TMPL.format(id_val=value.id, sub=subprop)
        results[subprop_key] = getattr(value, subprop)
      else:
        results[subprop] = value
    return results


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
    assert self.subproperties != [EMPTY_SUBPROPERTY_KEY]

  def get_property_for(self, instance):
    """Collect property for sended instance"""
    values = self.get_value_for(instance)
    results = {}
    for sub in self.subproperties:
      for value in values:
        if value is not None:
          sub_key = self.SUB_KEY_TMPL.format(id_val=value.id, sub=sub)
          results[sub_key] = getattr(value, sub)
        else:
          sub_key = self.SUB_KEY_TMPL.format(id_val='EMPTY', sub=sub)
          results[sub_key] = None
    return results
