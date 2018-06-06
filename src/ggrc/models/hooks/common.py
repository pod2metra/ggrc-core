# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Common logic for hooks."""

import sqlalchemy as sa

from ggrc import db
from ggrc.fulltext import mixin
from ggrc.models import all_models
from ggrc.models.mixins import attributable
from ggrc.utils import referenced_objects


def ensure_field_not_changed(obj, field_name):
  field_history = sa.inspect(obj).attrs[field_name].history
  if field_history.added or field_history.deleted:
    raise ValueError("{} field should not be changed".format(field_name))


def map_objects(src, dst):
  """Creates a relationship between an src and dst. This also
  generates automappings. Fails silently if dst dict does not have id and type
  keys.

  Args:
    src (model): The src model
    dst (dict): A dict with `id` and `type`.
  Returns:
    None
  """
  if not dst:
    return
  if 'id' not in dst or 'type' not in dst:
    return

  destination = referenced_objects.get(dst["type"], dst["id"])
  if not destination:
    raise ValueError("No {} with id {} found."
                     .format(dst["type"], dst["id"]))
  db.session.add(all_models.Relationship(
      source=src,
      destination=destination,
      context=src.context or destination.context,
  ))


def _handle_obj_delete(mapper, connection, target):
  """Clean fulltext and attributes tables from removed object data"""
  # pylint: disable=unused-argument
  delete_queries = []
  if issubclass(type(target), mixin.Indexed):
    for query in target.delete_queries_generator([target.id]):
      delete_queries.append(query)
  if issubclass(type(target), attributable.Attributable):
    delete_queries.append(target.get_delete_ca_query_for([target.id]))

  for query in delete_queries:
    if query is not None:
      db.session.execute(query)


def init_hook():
  """Initializes common hooks."""
  for model in all_models.all_models:
    sa.event.listen(model, "after_delete", _handle_obj_delete)
