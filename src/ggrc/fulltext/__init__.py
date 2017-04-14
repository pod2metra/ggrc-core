# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

from collections import defaultdict

from ggrc.extensions import get_extension_instance


class Indexer(object):

  def __init__(self, settings):
    self.indexer_rules = defaultdict(list)
    self.cache = defaultdict(dict)
    self.builders = {}

  def get_builder(self, obj_class):
    from .recordbuilder import RecordBuilder
    builder = self.builders.get(obj_class.__name__)
    if builder is not None:
      return builder
    builder = RecordBuilder(obj_class, self)
    self.builders[obj_class.__name__] = builder
    return builder

  def fts_record_for(self, obj):
    return self.get_builder(obj.__class__).as_record(obj)

  def invalidate_cache(self):
    self.cache = defaultdict(dict)

  def create_record(self, record):
    raise NotImplementedError()

  def update_record(self, record):
    raise NotImplementedError()

  def delete_record(self, key):
    raise NotImplementedError()

  def search(self, terms):
    raise NotImplementedError()


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
