# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

""" This module collects all indexer function required for indexed models."""

from collections import defaultdict

import itertools
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import select

from ggrc import db
from ggrc.fulltext.attributes import FullTextAttr
import ggrc.models
from ggrc.models.mixins import CustomAttributable
from ggrc.models.person import Person
from ggrc.models.reflection import AttributeInfo
import ggrc.query
from ggrc.rbac import context_query_filter
from ggrc.rbac import permissions
from ggrc.fulltext import mysql
from ggrc.fulltext import utils


indexer_rules = defaultdict(list)
indexer_fields = defaultdict(set)
cache = defaultdict(dict)
_cache_ft_attrs = {}


def get_ft_attrs(obj_class):
  """return recordbuilder for sent class

  save it in builders dict arguments and cache it here
  """
  if obj_class not in _cache_ft_attrs:
    _cache_ft_attrs[obj_class] = AttributeInfo.gather_attrs(
      obj_class,
      '_fulltext_attrs')
  return _cache_ft_attrs[obj_class]

def get_custom_attribute_properties(definition, value):
  """Get property value in case of indexing CA
  """
  # The name of the attribute property needs to be unique for each object,
  # the value comes from the custom_attribute_value
  attribute_name = definition.title
  properties = {}
  if value and definition.attribute_type == "Map:Person":
    properties[attribute_name] = build_person_subprops(value)
    properties[attribute_name].update(build_list_sort_subprop([value]))
  else:
    properties[attribute_name] = {"": definition.get_indexed_value(value)}
  return properties


def get_properties(obj):
  """Get indexable properties and values.

  Properties should be returned in the following format:
  {
    property1: {
      subproperty1: value1,
      subproperty2: value2,
      ...
    },
    ...
  }
  If there is no subproperty - empty string is used as a key
  """
  if obj.type == "Snapshot":
    # Snapshots do not have any indexable content. The object content for
    # snapshots is stored in the revision. Snapshots can also be made for
    # different models so we have to get fulltext attrs for the actual child
    # that was snapshotted and get data for those from the revision content.
    tgt_class = getattr(ggrc.models.all_models, obj.child_type, None)
    if not tgt_class:
      return {}
    attrs = get_ft_attrs(tgt_class)
    return {attr: {"": obj.revision.content.get(attr)} for attr in attrs}

  properties = {}
  property_tmpl = utils.get_property_tmpl(obj)

  for attr in get_ft_attrs(obj.__class__):
    if isinstance(attr, basestring):
      properties[property_tmpl.format(attr)] = {"": getattr(obj, attr)}
    elif isinstance(attr, FullTextAttr):
      properties.update(attr.get_property_for(obj))

  if isinstance(obj, CustomAttributable):
    cavs = {v.custom_attribute_id: v for v in obj.custom_attribute_values}
    for cad in obj.custom_attribute_definitions:
      cav = cavs.get(cad.id)
      if not cav:
        value = cad.default_value
      elif cad.attribute_type == "Map:Person":
        value = cav.attribute_object if cav.attribute_object_id else None
      else:
        value = cav.attribute_value
      properties.update(get_custom_attribute_properties(cad, value))
  return properties

def get_person_id_name_email(person):
  """Get id, name and email for person (either object or dict).

  If there is a global people map, get the data from it instead of the DB.
  """
  if isinstance(person, dict):
    person_id = person["id"]
  else:
    person_id = person.id
  if person_id in cache['people_map']:
    person_name, person_email = cache['people_map'][person_id]
  else:
    if isinstance(person, dict):
      person = db.session.query(Person).filter_by(
        id=person["id"]
      ).one()
    person_id = person.id
    person_name = person.name
    person_email = person.email
    cache['people_map'][person_id] = (person_name, person_email)
  return person_id, person_name, person_email

def get_ac_role_person_id(ac_list):
  """Get ac_role name and person name for ac_role (either object or dict).

  If there is a global ac_role map, get the data from it instead of the DB.
  """
  if isinstance(ac_list, dict):
    ac_role_id = ac_list["ac_role_id"]
    ac_person_id = ac_list["person_id"]
  else:
    ac_role_id = ac_list.ac_role_id
    ac_person_id = ac_list.person_id
  if ac_role_id not in cache['ac_role_map']:
    ac_role = db.session.query(
        ggrc.models.all_models.AccessControlRole
    ).get(
        ac_role_id
    )
    # Internal roles should not be indexed
    if ac_role and ac_role.internal:
      cache['ac_role_map'][ac_role_id] = None
    else:
      ac_role_name = ac_role.name if ac_role else None
      cache['ac_role_map'][ac_role_id] = ac_role_name
      if ac_role_name is None:
        # index only existed role, if it have already been
        # removed than nothing to index.
        LOGGER.error(
          "Trying to index not existing ACR with id %s", ac_role_id
        )
  ac_role_name = cache['ac_role_map'][ac_role_id]
  if ac_role_name:
    ac_role_name = ac_role_name.lower()
  return ac_role_name, ac_person_id

def build_person_subprops(person):
  """Get dict of Person properties for fulltext indexing

  If Person provided by Revision, need to go to DB to get Person data
  """
  subproperties = {}
  person_id, person_name, person_email = get_person_id_name_email(
    person
  )
  subproperties["{}-email".format(person_id)] = person_email
  subproperties["{}-name".format(person_id)] = person_name
  return subproperties

def build_list_sort_subprop(people):
  """Get a special subproperty for sorting.

  Its content is :-separated sorted list of (name or email) of the people in
  list.
  """
  if not people:
    return {"__sort__": ""}
  _, _, emails = zip(*(get_person_id_name_email(p) for p in people))
  content = ":".join(sorted(emails))
  return {"__sort__": content}

def invalidate_cache():
  global cache
  cache = defaultdict(dict)

def records_generator( obj):
  """Record generator method."""
  for prop, value in get_properties(obj).iteritems():
    for subproperty, content in value.items():
      if content is not None:
        yield mysql.MysqlRecordProperty(
          key=obj.id,
          type=obj.type,
          context_id=obj.context_id,
          tags="",
          property=prop,
          subproperty=unicode(subproperty),
          content=unicode(content),
        )

def create_record(obj, commit=True):
  """Create records in db."""
  for record in records_generator(obj):
    db.session.add(record)
  if commit:
    db.session.commit()

def update_record(instance, commit=True):
  """Update records values in db."""
  # remove the obsolete index entries
  delete_record(instance, False)
  create_record(instance, commit)

def delete_record(instance, commit=True):
  """Delete records values in db for specific types."""
  db.session.query(mysql.MysqlRecordProperty).filter(
    mysql.MysqlRecordProperty.key == instance.id,
    mysql.MysqlRecordProperty.type == instance.type,
    ).delete()
  if commit:
    db.session.commit()

def delete_records_by_ids(type, keys, commit=True):
  """Method to delete all records related to type and keys."""
  if not keys:
    return
  db.session.query(
    mysql.MysqlRecordProperty
  ).filter(
    mysql.MysqlRecordProperty.key.in_(keys),
    mysql.MysqlRecordProperty.type == type,
    ).delete(
    synchronize_session="fetch"
  )
  if commit:
    db.session.commit()

def _get_filter_query(terms):
  """Get the whitelist of fields to filter in full text table."""
  whitelist = mysql.MysqlRecordProperty.property.in_(
    ['title', 'name', 'email', 'notes', 'description', 'slug'])

  if not terms:
    return whitelist
  elif terms:
    return sa.and_(whitelist, mysql.MysqlRecordProperty.content.contains(terms))

def get_permissions_query(model_names, permission_type='read',
                          permission_model=None):
  """Prepare the query based on the allowed contexts and resources for
   each of the required objects(models).
  """
  if not model_names:
    # If there are no model names set, the result of the permissions query
    # will always be false, so we can just return false instead of having an
    # empty in statement combined with an empty list joined by or statement.
    return sa.false()

  type_queries = []
  for model_name in model_names:
    contexts, resources = permissions.get_context_resource(
      model_name=model_name,
      permission_type=permission_type,
      permission_model=permission_model
    )
    statement = sa.and_(
      mysql.MysqlRecordProperty.type == model_name,
      context_query_filter(mysql.MysqlRecordProperty.context_id, contexts)
    )
    if resources:
      statement = sa.or_(sa.and_(mysql.MysqlRecordProperty.type == model_name,
                                 mysql.MysqlRecordProperty.key.in_(resources)),
                         statement)
    type_queries.append(statement)

  return sa.and_(
    mysql.MysqlRecordProperty.type.in_(model_names),
    sa.or_(*type_queries)
  )

def search_get_owner_query(query, types=None, contact_id=None):
  """Prepare the search query based on the contact_id to return my
  objects. This method is used only for dashboard and returns objects
  the user is the owner.
  """
  if not contact_id:
    return query

  union_query = ggrc.query.my_objects.get_myobjects_query(
    types=types,
    contact_id=contact_id)

  return query.join(
    union_query,
    sa.and_(
      union_query.c.id == mysql.MysqlRecordProperty.key,
      union_query.c.type == mysql.MysqlRecordProperty.type),
  )

def _add_extra_params_query(query, type_name, extra_param):
  """Prepare the query for handling extra params."""
  if not extra_param:
    return query

  models = [m for m in ggrc.models.all_models.all_models
            if m.__name__ == type_name]

  if len(models) == 0:
    return query
  model_klass = models[0]

  return query.filter(mysql.MysqlRecordProperty.key.in_(
    db.session.query(
      model_klass.id.label('id')
    ).filter_by(**extra_param)
  ))

def _get_grouped_types(types=None, extra_params=None):
  """Return list of model names from all model names

  if they in sended types and extra_params"""
  model_names = []
  for model_klass in ggrc.models.all_models.all_models:
    model_name = model_klass.__name__
    if types and model_name not in types:
      continue
    if extra_params and model_name in extra_params:
      continue
    model_names.append(model_name)
  return model_names

def search(terms, types=None, permission_type='read',
           permission_model=None, contact_id=None, extra_params=None):
  """Prepare the search query and return the results set based on the
  full text table."""
  extra_params = extra_params or {}
  model_names = _get_grouped_types(types, extra_params)
  columns = (
    mysql.MysqlRecordProperty.key.label('key'),
    mysql.MysqlRecordProperty.type.label('type'),
    mysql.MysqlRecordProperty.property.label('property'),
    mysql.MysqlRecordProperty.content.label('content'),
    sa.case(
      [(mysql.MysqlRecordProperty.property == 'title', sa.literal(0))],
      else_=sa.literal(1)
    ).label('sort_key'))

  query = db.session.query(*columns)
  query = query.filter(get_permissions_query(
    model_names, permission_type, permission_model))
  query = query.filter(_get_filter_query(terms))
  query = search_get_owner_query(query, types, contact_id)

  model_names = _get_grouped_types(types)

  unions = [query]
  # Add extra_params and extra_colums:
  for key, value in extra_params.iteritems():
    if key not in model_names:
      continue
    extra_q = db.session.query(*columns)
    extra_q = extra_q.filter(
      get_permissions_query([key], permission_type, permission_model))
    extra_q = extra_q.filter(_get_filter_query(terms))
    extra_q = search_get_owner_query(extra_q, [key], contact_id)
    extra_q = _add_extra_params_query(extra_q, key, value)
    unions.append(extra_q)
  all_queries = sa.union(*unions)
  all_queries = aliased(all_queries.order_by(
    all_queries.c.sort_key, all_queries.c.content))
  return db.session.execute(
    select([all_queries.c.key, all_queries.c.type]).distinct())

def counts(terms, types=None, contact_id=None,
           extra_params=None, extra_columns=None):
  """Prepare the search query, but return only count for each of
   the requested objects."""
  extra_params = extra_params or {}
  extra_columns = extra_columns or {}
  model_names = _get_grouped_types(types, extra_params)
  query = db.session.query(
    mysql.MysqlRecordProperty.type,
    sa.func.count(sa.distinct(
      mysql.MysqlRecordProperty.key)), sa.literal(""))
  query = query.filter(get_permissions_query(model_names))
  query = query.filter(_get_filter_query(terms))
  query = search_get_owner_query(query, types, contact_id)
  query = query.group_by(mysql.MysqlRecordProperty.type)
  all_extra_columns = dict(extra_columns.items() +
                           [(p, p) for p in extra_params
                            if p not in extra_columns])
  if not all_extra_columns:
    return query.all()

  # Add extra_params and extra_colums:
  for key, value in all_extra_columns.iteritems():
    extra_q = db.session.query(
      mysql.MysqlRecordProperty.type,
      sa.func.count(sa.distinct(mysql.MysqlRecordProperty.key)),
      sa.literal(key)
    )
    extra_q = extra_q.filter(get_permissions_query([value]))
    extra_q = extra_q.filter(_get_filter_query(terms))
    extra_q = search_get_owner_query(extra_q, [value], contact_id)
    extra_q = _add_extra_params_query(extra_q,
                                      value,
                                      extra_params.get(key, None))
    extra_q = extra_q.group_by(mysql.MysqlRecordProperty.type)
    query = query.union(extra_q)
  return query.all()

def get_insert_query_for(cls, ids):
  """Return insert class record query. It will return None, if it's empty."""
  if not ids:
    return
  instances = cls.indexed_query().filter(cls.id.in_(ids))
  keys = inspect(mysql.MysqlRecordProperty).c
  rows = itertools.chain(*[records_generator(i) for i in instances])
  values = [{c.name: getattr(r, a) for a, c in keys.items()} for r in rows]
  if not values:
    return None
  return mysql.MysqlRecordProperty.__table__.insert().values(values)

def get_delete_query_for(cls, ids):
  """Return delete class record query. If ids are empty, will return None."""
  if not ids:
    return
  return mysql.MysqlRecordProperty.__table__.delete().where(
    mysql.MysqlRecordProperty.type == cls.__name__
  ).where(
    mysql.MysqlRecordProperty.key.in_(ids)
  )

def bulk_record_update_for(cls, ids):
  """Bulky update index records for current class"""
  delete_query = get_delete_query_for(cls, ids)
  insert_query = get_insert_query_for(cls, ids)
  for query in [delete_query, insert_query]:
    if query is not None:
      db.session.execute(query)

