from collections import defaultdict

from sqlalchemy import event

from ggrc import db
from ggrc.models.inflector import get_model
from ggrc.fulltext import indexer
from ggrc.fulltext import listeners


def init_hooks():
  @event.listens_for(db.session.__class__, 'before_commit')
  def update_indexer(session):  # pylint:disable=unused-argument
    """General function to update index

    for all updated related instance before commit"""

    if not hasattr(db.session, "reindex_set"):
      return

    models_ids_to_reindex = defaultdict(set)
    db.session.flush()
    for for_index in db.session.reindex_set:
      if for_index not in db.session:
        continue
      type_name, id_value = for_index.get_reindex_pair()
      if type_name:
        models_ids_to_reindex[type_name].add(id_value)
    db.session.expire_all()  # expire required to fix declared_attr cached value
    db.session.reindex_set.invalidate()
    for model_name, ids in models_ids_to_reindex.iteritems():
      indexer.bulk_record_update_for(get_model(model_name), ids)

  listeners.register_fulltext_listeners()
