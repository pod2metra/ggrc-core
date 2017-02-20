# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

from ggrc.extensions import get_extension_instance


class Indexer(object):

  def __init__(self, settings):
    pass

  def create_record(self, record):
    raise NotImplementedError()

  def update_record(self, record):
    raise NotImplementedError()

  def delete_record(self, key):
    raise NotImplementedError()

  def search(self, terms):
    raise NotImplementedError()


class Record(object):

  def __init__(self, key, rec_type, context_id, properties, tags=""):
    self.key = key
    self.type = rec_type
    self.context_id = context_id
    self.tags = tags
    self.properties = properties

EMPY_SUBPROPERTY_KEY = ''


class FullTextAttr(object):

  def __init__(self, alias, value, subproperties=None):
    self.alias = alias
    self.value = value
    self.subproperties = subproperties or [EMPY_SUBPROPERTY_KEY]

  def get_value_for(self, instance):
    if callable(self.value):
      return self.value(instance)
    return getattr(instance, self.value)

  def get_property_for(self, instance):
    value = self.get_value_for(instance)
    results = {}
    for subprop in self.subproperties:
      if value is not None and subprop != EMPY_SUBPROPERTY_KEY:
        value = getattr(value, subprop)
      results[subprop] = value
    return results


class MultipleSubpropertyFullTextAttr(FullTextAttr):

  SUB_KEY_TMPL = "{id_val}-{sub}"

  def __init__(self, alias, value, subproperties):
    assert subproperties
    super(MultipleSubpropertyFullTextAttr, self).__init__(
        alias, value, subproperties
    )

  def get_property_for(self, instance):
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


def resolve_default_text_indexer():
  from ggrc import settings
  db_scheme = settings.SQLALCHEMY_DATABASE_URI.split(':')[0].split('+')[0]
  return 'ggrc.fulltext.{db_scheme}.Indexer'.format(db_scheme=db_scheme)


def get_indexer(indexer=[]):
  return get_extension_instance(
      'FULLTEXT_INDEXER', resolve_default_text_indexer)


def get_indexed_model_names():
  return {
      "AccessGroup",
      "Assessment",
      "AssessmentTemplate",
      "Audit",
      "Clause",
      "Comment",
      "Contract",
      "Control",
      "Cycle",
      "CycleTaskEntry",
      "CycleTaskGroup",
      "CycleTaskGroupObjectTask",
      "CustomAttributeValue",  # needed because of indexing logic
      "DataAsset",
      "Facility",
      "Issue",
      "Market",
      "Objective",
      "OrgGroup",
      "Person",
      "Policy",
      "Process",
      "Product",
      "Program",
      "Project",
      "Regulation",
      "Risk",
      "RiskAssessment",
      "Section",
      "Standard",
      "System",
      "TaskGroup",
      "TaskGroupTask",
      "Threat",
      "Vendor",
      "Workflow",
  }
