# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

from collections import defaultdict, Iterable

from sqlalchemy import and_
from sqlalchemy import case
from sqlalchemy import distinct
from sqlalchemy import func
from sqlalchemy import literal
from sqlalchemy import or_
from sqlalchemy import union
from sqlalchemy.sql import false
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import aliased
from sqlalchemy import event
from sqlalchemy.sql.expression import select
from ggrc import db
from ggrc.login import is_creator
from ggrc.models import all_models
from ggrc.utils import query_helpers
from ggrc.rbac import context_query_filter
from ggrc.fulltext.sql import SqlIndexer
from ggrc.fulltext.mixin import Indexed


class MysqlRecordProperty(db.Model):
  __tablename__ = 'fulltext_record_properties'

  key = db.Column(db.Integer, primary_key=True)
  type = db.Column(db.String(64), primary_key=True)
  context_id = db.Column(db.Integer)
  tags = db.Column(db.String)
  property = db.Column(db.String(250), primary_key=True)
  subproperty = db.Column(db.String(64), primary_key=True)
  content = db.Column(db.Text)

  @declared_attr
  def __table_args__(self):
    return (
        db.Index('ix_{}_tags'.format(self.__tablename__), 'tags'),
        db.Index('ix_{}_key'.format(self.__tablename__), 'key'),
        db.Index('ix_{}_type'.format(self.__tablename__), 'type'),
        db.Index('ix_{}_context_id'.format(self.__tablename__), 'context_id'),
    )


class MysqlIndexer(SqlIndexer):
  record_type = MysqlRecordProperty

  def _get_filter_query(self, terms):
    """Get the whitelist of fields to filter in full text table."""
    whitelist = MysqlRecordProperty.property.in_(
        ['title', 'name', 'email', 'notes', 'description', 'slug'])

    if not terms:
      return whitelist
    elif terms:
      return and_(whitelist, MysqlRecordProperty.content.contains(terms))

  def get_permissions_query(self, model_names, permission_type='read',
                            permission_model=None):
    """Prepare the query based on the allowed contexts and resources for
     each of the required objects(models).
    """
    type_queries = []
    for model_name in model_names:
      contexts, resources = query_helpers.get_context_resource(
          model_name=model_name,
          permission_type=permission_type,
          permission_model=permission_model
      )
      if contexts is not None:
        if resources:
          resource_sql = and_(
              MysqlRecordProperty.type == model_name,
              MysqlRecordProperty.key.in_(resources))
        else:
          resource_sql = false()

        type_query = or_(
            and_(
                MysqlRecordProperty.type == model_name,
                context_query_filter(MysqlRecordProperty.context_id, contexts)
            ),
            resource_sql)
        type_queries.append(type_query)

    return and_(
        MysqlRecordProperty.type.in_(model_names),
        or_(*type_queries))

  def search_get_owner_query(self, query, types=None, contact_id=None):
    """Prepare the search query based on the contact_id to return my
    objects. This method is used only for dashboard and returns objects
    the user is the owner.
    """
    if not contact_id:
      return query

    union_query = query_helpers.get_myobjects_query(
        types=types,
        contact_id=contact_id,
        is_creator=is_creator()
    )

    return query.join(
        union_query,
        and_(
            union_query.c.id == MysqlRecordProperty.key,
            union_query.c.type == MysqlRecordProperty.type),
    )

  def _add_extra_params_query(self, query, type, extra_param):
    """Prepare the query for handling extra params."""
    if not extra_param:
      return query

    models = [m for m in all_models.all_models if m.__name__ == type]

    if len(models) == 0:
      return query
    model = models[0]

    return query.filter(self.record_type.key.in_(
        db.session.query(
            model.id.label('id')
        ).filter_by(**extra_param)
    ))

  def _get_grouped_types(self, types, extra_params=None):
    model_names = [model.__name__ for model in all_models.all_models]
    if types is not None:
      model_names = [m for m in model_names if m in types]

    if extra_params is not None:
      model_names = [m for m in model_names if m not in extra_params]
    return model_names

  def search(self, terms, types=None, permission_type='read',
             permission_model=None, contact_id=None, extra_params={}):
    """Prepare the search query and return the results set based on the
    full text table."""
    model_names = self._get_grouped_types(types, extra_params)
    columns = (
        self.record_type.key.label('key'),
        self.record_type.type.label('type'),
        self.record_type.property.label('property'),
        self.record_type.content.label('content'),
        case(
            [(self.record_type.property == 'title', literal(0))],
            else_=literal(1)).label('sort_key'))

    query = db.session.query(*columns)
    query = query.filter(self.get_permissions_query(
        model_names, permission_type, permission_model))
    query = query.filter(self._get_filter_query(terms))
    query = self.search_get_owner_query(query, types, contact_id)

    model_names = [model.__name__ for model in all_models.all_models]
    if types is not None:
      model_names = [m for m in model_names if m in types]

    unions = [query]
    # Add extra_params and extra_colums:
    for key, value in extra_params.iteritems():
      if key not in model_names:
        continue
      extra_q = db.session.query(*columns)
      extra_q = extra_q.filter(
          self.get_permissions_query([key], permission_type, permission_model))
      extra_q = extra_q.filter(self._get_filter_query(terms))
      extra_q = self.search_get_owner_query(extra_q, [key], contact_id)
      extra_q = self._add_extra_params_query(extra_q, key, value)
      unions.append(extra_q)
    all_queries = union(*unions)
    all_queries = aliased(all_queries.order_by(
        all_queries.c.sort_key, all_queries.c.content))
    return db.session.execute(
        select([all_queries.c.key, all_queries.c.type]).distinct())

  def counts(self, terms, types=None, contact_id=None,
             extra_params={}, extra_columns={}):
    """Prepare the search query, but return only count for each of
     the requested objects."""
    model_names = self._get_grouped_types(types, extra_params)
    query = db.session.query(
        self.record_type.type, func.count(distinct(
            self.record_type.key)), literal(""))
    query = query.filter(self.get_permissions_query(model_names))
    query = query.filter(self._get_filter_query(terms))
    query = self.search_get_owner_query(query, types, contact_id)
    query = query.group_by(self.record_type.type)
    all_extra_columns = dict(extra_columns.items() +
                             [(p, p) for p in extra_params
                              if p not in extra_columns])
    if not all_extra_columns:
      return query.all()

    for key, value in all_extra_columns.iteritems():
      extra_q = db.session.query(self.record_type.type,
                                 func.count(distinct(self.record_type.key)),
                                 literal(key))
      extra_q = extra_q.filter(self.get_permissions_query([value]))
      extra_q = extra_q.filter(self._get_filter_query(terms))
      extra_q = self.search_get_owner_query(extra_q, [value], contact_id)
      extra_q = self._add_extra_params_query(extra_q,
                                             value,
                                             extra_params.get(key, None))
      extra_q = extra_q.group_by(self.record_type.type)
      query = query.union(extra_q)
    return query.all()

Indexer = MysqlIndexer


INDEXER_RULES = defaultdict(list)

for model in all_models.all_models:
  if issubclass(model, Indexed):
    for rule in model.AUTO_REINDEX_RULES:
      INDEXER_RULES[rule.model].append(rule.rule)


@event.listens_for(db.session.__class__, 'before_commit')
def update_indexer(session):
  """General function to update index

  for all updated related instance before commit"""

  reindex_dict = {}
  for instance in session.dirty:
    getters = INDEXER_RULES.get(instance.__class__.__name__) or []
    for getter in getters:
      to_index_list = getter(instance)
      if not isinstance(to_index_list, Iterable):
        to_index_list = [to_index_list]
      for to_index in to_index_list:
        key = "{}-{}".format(to_index.__class__.__name__, to_index.id)
        reindex_dict[key] = to_index
  for for_index in reindex_dict.values():
    for_index.update_indexer()
