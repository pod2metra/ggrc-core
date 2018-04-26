# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Fulltext event listeners"""

from collections import Iterable
import threading

import sqlalchemy as sa
from sqlalchemy import event

from ggrc import db
from ggrc import fulltext
from ggrc.models import all_models
from ggrc.fulltext import mixin


ACTIONS = ['after_insert', 'after_delete', 'after_update']


class ReindexSet(threading.local):
  """Special thread safety object.

   That will collect pool of objects that required to be reindexed."""

  def __init__(self, *args, **kwargs):
    super(ReindexSet, self).__init__(*args, **kwargs)
    self._pool = set()

  def add(self, item):
    self._pool.add(item)

  def __iter__(self):
    return iter(self._pool)

  def invalidate(self):
    self._pool = set()


def _runner(mapper, content, target):  # pylint:disable=unused-argument
  """Collect all reindex models in session"""
  db.session.reindex_set = getattr(db.session, "reindex_set", ReindexSet())
  getters = fulltext.indexer.indexer_rules.get(target.__class__.__name__) or []
  fields = fulltext.indexer.indexer_fields.get(target.__class__.__name__)
  for getter in getters:
    if fields and not fields_changed(target, fields):
      continue
    to_index_list = getter(target)
    if not isinstance(to_index_list, Iterable):
      to_index_list = [to_index_list]
    for to_index in to_index_list:
      db.session.reindex_set.add(to_index)
  if isinstance(target, mixin.Indexed):
    db.session.reindex_set.add(target)


def register_fulltext_listeners():
  """Indexing initialization procedure"""
  for model in all_models.all_models:
    for action in ACTIONS:
      event.listen(model, action, _runner)
    if not issubclass(model, mixin.Indexed):
      continue
    for sub_model in model.mro():
      for rule in getattr(sub_model, "AUTO_REINDEX_RULES", []):
        fulltext.indexer.indexer_rules[rule.model].append(rule.rule)
        if rule.fields:
          fulltext.indexer.indexer_fields[rule.model].update(rule.fields)


def fields_changed(obj, fields):
  """Check if any of object fields were changed"""
  for field in fields:
    if getattr(sa.inspect(obj).attrs, field).history.has_changes():
      return True
  return False
