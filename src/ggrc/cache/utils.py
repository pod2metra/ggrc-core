# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Common operations on cache managers."""

import logging

import flask

from ggrc import cache
import ggrc.models
from ggrc import settings

logger = logging.getLogger(__name__)


def get_cache_manager():
    """Returns an instance of CacheManager."""
    cache_manager = cache.CacheManager()
    cache_manager.initialize(cache.MemCache())
    return cache_manager


def get_cache_key(obj, type_=None, id_=None):
    """Returns a string identifier for the specified object or stub.

  `obj` can be:
    <db.Model> -- declarative model instance
    (type, id) -- tuple
    { 'type': type, 'id': id } -- dict
  """
    if isinstance(obj, tuple):
        type_, id_ = obj
    elif isinstance(obj, dict):
        type_ = obj.get('type', None)
        id_ = obj.get('id', None)
    if isinstance(type_, (str, unicode)):
        model = ggrc.models.get_model(type_)
        assert model is not None, "Invalid model name: {}".format(type_)
        type_ = ggrc.models.get_model(type_)._inflector.table_plural
    if not isinstance(obj, (tuple, dict)):
        if type_ is None:
            type_ = obj._inflector.table_plural
        if id_ is None:
            id_ = obj.id
    return 'collection:{type_}:{id_}'.format(type_=type_, id_=id_)


def get_cache_class(obj):
    """Returns string name of object's class."""
    return obj.__class__.__name__


def get_related_keys_for_expiration(context, o):
    """Returns a list for expiration."""
    cls = get_cache_class(o)
    keys = []
    mappings = context.cache_manager.supported_mappings.get(cls, [])

    for (cls, attr, polymorph) in mappings:
        if polymorph:
            key = get_cache_key(
                None,
                type_=getattr(o, '{0}_type'.format(attr)),
                id_=getattr(o, '{0}_id'.format(attr)))
            keys.append(key)
        else:
            obj = getattr(o, attr, None)
            if obj:
                if isinstance(obj, list):
                    for inner_o in obj:
                        key = get_cache_key(inner_o)
                        keys.append(key)
                else:
                    key = get_cache_key(obj)
                    keys.append(key)
    return keys


def memcache_mark_for_deletion(context, objects_to_mark):
    """
  Mark objects for deletion from memcache

  Args:
    context: application context
    objects_to_mark: A list of objects to be deleted from memcache

  Returns:
    None
  """
    for o, _ in objects_to_mark:
        cls = get_cache_class(o)
        if cls in context.cache_manager.supported_classes:
            key = get_cache_key(o)
            context.cache_manager.marked_for_delete.append(key)
            context.cache_manager.marked_for_delete.extend(
                get_related_keys_for_expiration(context, o))


def update_memcache_before_commit(context, modified_objects, expiry_time):
    """
  Preparing the memccache entries to be updated before DB commit
  Also update the memcache to indicate the status cache operation
  'InProgress' waiting for DB commit
  Raises Exception on failures, cannot proceed with DB commit

  Args:
    context: POST/PUT/DELETE HTTP request or import Converter contextual object
    modified_objects:  objects in cache maintained prior to committing to DB
    expiry_time: Expiry time specified for memcache ADD and DELETE
  Returns:
    None

  """
    if getattr(settings, 'MEMCACHE_MECHANISM', False) is False:
        return

    context.cache_manager = get_cache_manager()

    if modified_objects is not None:
        if modified_objects.new:
            memcache_mark_for_deletion(context, modified_objects.new.items())

        if modified_objects.dirty:
            memcache_mark_for_deletion(context, modified_objects.dirty.items())

        if modified_objects.deleted:
            memcache_mark_for_deletion(context,
                                       modified_objects.deleted.items())

    status_entries = {}
    for key in context.cache_manager.marked_for_delete:
        build_cache_status(status_entries, 'DeleteOp:' + key, expiry_time,
                           'InProgress')
    if status_entries:
        logger.info("CACHE: status entries: %s", status_entries)
        ret = context.cache_manager.bulk_add(status_entries, expiry_time)
        if ret is not None and not ret:
            pass
        else:
            logger.error(
                'CACHE: Unable to add status for newly created entries %s',
                ret)


def update_memcache_after_commit(context):
    """
  The memccache entries is updated after DB commit
  Logs error if there are errors in updating entries in cache

  Args:
    context: POST/PUT/DELETE HTTP request or import Converter contextual object
    modified_objects:  objects in cache maintained prior to committing to DB
  Returns:
    None

  """
    if getattr(settings, 'MEMCACHE_MECHANISM', False) is False:
        return

    if context.cache_manager is None:
        logger.error("CACHE: Error in initiaizing cache manager")
        return

    cache_manager = context.cache_manager

    related_objs = list()
    for val in getattr(flask.g, "referenced_objects", {}).itervalues():
        obj_list = val.values()
        if obj_list:
            related_objs.append((obj_list[0], None))
    memcache_mark_for_deletion(context, related_objs)

    # TODO(dan): check for duplicates in marked_for_delete
    if cache_manager.marked_for_delete:
        delete_result = cache_manager.bulk_delete(
            cache_manager.marked_for_delete, 0)
        # TODO(dan): handling failure including network errors,
        #            currently we log errors
        if delete_result is not True:
            logger.error("CACHE: Failed to remove collection from cache")

    status_entries = []
    for key in cache_manager.marked_for_delete:
        status_entries.append('DeleteOp:' + str(key))
    if status_entries:
        delete_result = cache_manager.bulk_delete(status_entries, 0)
        # TODO(dan): handling failure including network errors,
        #            currently we log errors
        if delete_result is not True:
            logger.error("CACHE: Failed to remove status entries from cache")

    clear_permission_cache()
    cache_manager.clear_cache()


def build_cache_status(data, key, expiry_timeout, status):
    """
  Build the dictionary for storing operational status of cache

  Args:
    data: dictionary to update
    key: key to dictionary
    expiry_timeout: timeout for expiry cache
    status: Update status entry, e.g.InProgress
  Returns:
    None
  """
    data[key] = {'expiry': expiry_timeout, 'status': status}


def clear_permission_cache():
    """Drop cached permissions for all users."""
    if not getattr(settings, 'MEMCACHE_MECHANISM', False):
        return
    client = get_cache_manager().cache_object.memcache_client
    cached_keys_set = client.get('permissions:list') or set()
    cached_keys_set.add('permissions:list')
    # We delete all the cached user permissions as well as
    # the permissions:list value itself
    client.delete_multi(cached_keys_set)
