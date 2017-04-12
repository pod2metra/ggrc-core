# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Full text index engine for Mysql DB backend"""
from collections import defaultdict

from sqlalchemy import and_
from sqlalchemy import case
from sqlalchemy import distinct
from sqlalchemy import func
from sqlalchemy import literal
from sqlalchemy import or_
from sqlalchemy import union
from sqlalchemy.sql import false
from sqlalchemy.schema import DDL
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import select
from sqlalchemy import event

from ggrc import db
from ggrc.login import is_creator
from ggrc.models import all_models
from ggrc.utils import query_helpers
from ggrc.rbac import context_query_filter
from ggrc.fulltext.sql import SqlIndexer


class MysqlRecordProperty(db.Model):
  """ Db model for collect fulltext index records"""
  __tablename__ = 'fulltext_record_properties'

  key = db.Column(db.Integer, primary_key=True)
  type = db.Column(db.String(64), primary_key=True)
  context_id = db.Column(db.Integer)
  tags = db.Column(db.String)
  property = db.Column(db.String(64), primary_key=True)
  subproperty = db.Column(db.String(64), primary_key=True)
  content = db.Column(db.Text)

  @declared_attr
  def __table_args__(self):
    return (
        # NOTE
        # This is here to prevent Alembic from wanting to drop the index, but
        # the DDL below or a similar Alembic migration should be used to create
        # the index.
        db.Index('{}_text_idx'.format(self.__tablename__), 'content'),
        # These are real indexes
        db.Index('ix_{}_key'.format(self.__tablename__), 'key'),
        db.Index('ix_{}_type'.format(self.__tablename__), 'type'),
        db.Index('ix_{}_tags'.format(self.__tablename__), 'tags'),
        db.Index('ix_{}_context_id'.format(self.__tablename__), 'context_id'),
        # Only MyISAM supports fulltext indexes until newer MySQL/MariaDB
        {'mysql_engine': 'myisam'},
    )


event.listen(
    MysqlRecordProperty.__table__,
    'after_create',
    DDL('ALTER TABLE {tablename} ADD FULLTEXT INDEX {tablename}_text_idx '
        '(content)'.format(tablename=MysqlRecordProperty.__tablename__))
)


class MysqlIndexer(SqlIndexer):
  record_type = MysqlRecordProperty

  @staticmethod
  def _get_filter_query(terms):
    """Get the whitelist of fields to filter in full text table."""
    whitelist = MysqlRecordProperty.property.in_(
        ['title', 'name', 'email', 'notes', 'description', 'slug'])

    if not terms:
      return whitelist
    elif terms:
      return and_(whitelist, MysqlRecordProperty.content.contains(terms))

  @staticmethod
  def get_permissions_query(model_names, permission_type='read',
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

  @staticmethod
  def search_get_owner_query(query, types=None, contact_id=None):
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

  def _add_extra_params_query(self, query, type_name, extra_param):
    """Prepare the query for handling extra params."""
    if not extra_param:
      return query

    models = [m for m in all_models.all_models if m.__name__ == type_name]

    if len(models) == 0:
      return query
    model_klass = models[0]

    return query.filter(self.record_type.key.in_(
        db.session.query(
            model_klass.id.label('id')
        ).filter_by(**extra_param)
    ))

  @staticmethod
  def _get_grouped_types(types=None, extra_params=None):
    """Return list of model names from all model names

    if they in sended types and extra_params"""
    model_names = []
    for model_klass in all_models.all_models:
      model_name = model_klass.__name__
      if types and model_name not in types:
        continue
      if extra_params and model_name in extra_params:
        continue
      model_names.append(model_name)
    return model_names

  def search(self, terms, types=None, permission_type='read',
             permission_model=None, contact_id=None, extra_params=None):
    """Prepare the search query and return the results set based on the
    full text table."""
    extra_params = extra_params or {}
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

    model_names = self._get_grouped_types(types)

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
             extra_params=None, extra_columns=None):
    """Prepare the search query, but return only count for each of
     the requested objects."""
    extra_params = extra_params or {}
    extra_columns = extra_columns or {}
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

    # Add extra_params and extra_colums:
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


@event.listens_for(db.session.__class__, 'before_commit')
def update_indexer(session):  # pylint:disable=unused-argument
  """General function to update index

  for all updated related instance before commit"""

  db.session.flush()
  models_ids_to_reindex = defaultdict(set)
  for for_index in getattr(db.session, 'reindex_set', set()):
    if for_index not in db.session:
      continue
    models_ids_to_reindex[for_index.__class__].add(for_index.id)
  db.session.reindex_set = set()
  for model, ids in models_ids_to_reindex.iteritems():
    for instance in model.indexed_query().filter(model.id.in_(ids)).all():
      instance.update_indexer()
