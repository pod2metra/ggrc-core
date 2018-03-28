# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
    CacheManager provides encapsulation to the caching mechanism used in GGRC
    for resource collection.

"""
from cache import all_cache_entries, all_mapping_entries


class CacheManager:
    """Cache manager provides encapsulation to caching mechanism such as
  Memcache.

  Attributes:
    cache: Ordered dictionary of all cache objects derived from base class
           (Cache)
    supported_classes: Model plural table name for a supported resource type
    supported_mappings: Mapping entry tuples for a supported resource type
    factory: Factory class to create cache object
    new, dirty, deleted: temporary dictionaries used in session event listeners
                         before and after flush
    marked_for_<op>: dictionaries used in session event listeners after flush,
                     before and after commit

  Returns:
    None
  """
    factory = None

    def __init__(self):
        pass

    def initialize(self, cache):
        """Initialize Cache Manager, configure cache mechanism."""
        self.supported_classes = {}
        for cache_entry in all_cache_entries():
            self.supported_classes[
                cache_entry.class_name] = cache_entry.model_plural

        self.supported_mappings = {}
        for mapping_entry in all_mapping_entries():
            self.supported_mappings.setdefault(mapping_entry.class_name, [])
            self.supported_mappings[mapping_entry.class_name].append(
                mapping_entry)

        self.cache_object = cache

        self.new = {}
        self.dirty = {}
        self.deleted = {}
        self.marked_for_add = {}
        self.marked_for_update = {}
        self.marked_for_delete = []

    def get_collection(self, category, resource, filter):
        """Get collection from cache.

    Args:
      category: collection or stub
      resource: regulation, controls, etc.
      filter: dictionary containing ids and optional attrs

    Returns:
      JSON string representation
    """
        if not self.is_caching_supported(category, resource, filter,
                                         'get_collection'):
            return None
        ret = self.cache_object.get(category, resource, filter)
        return ret

    def add_collection(self, category, resource, data, expiration_time=0):
        """Add collection in cache.

    Args:
      category: collection or stub
      resource: regulation, controls, etc.
      data: dictionary containing ids and attrs to update
    Returns:
     DTO formatted string, e.g. JSON string representation
    """

        if not self.is_caching_supported(category, resource, data,
                                         'add_collection'):
            return None
        ret = self.cache_object.add(category, resource, data, expiration_time)
        return ret

    def update_collection(self, category, resource, data, expiration_time=0):
        """Update collection in cache.

    Args:
      category: collection or stub
      resource: regulation, controls, etc.
      data: dictionary containing ids and attrs to update
    Returns:
     JSON string representation
    """
        if not self.is_caching_supported(category, resource, data,
                                         'update_collection'):
            return None
        ret = self.cache_object.update(category, resource, data,
                                       expiration_time)
        return ret

    def delete_collection(self, category, resource, data, lockadd_seconds=0):
        """Delete collection from cache.

    Args:
      category: collection or stub
      resource: regulation, controls, etc.
      data: dictionary containing ids of the resource to delete
    Returns:
      JSON string representation
    """
        if not self.is_caching_supported(category, resource, data,
                                         'delete_collection'):
            return None

        ret = self.cache_object.remove(category, resource, data,
                                       lockadd_seconds)
        return ret

    def is_caching_supported(self,
                             category,
                             resource,
                             data=None,
                             operation=None):
        """Check if caching is supported.

    Args:
      category: collection or stub
      resource: regulation, controls, etc.
      data: additional data such as context information, Default is None
      operation: operation performed such as get, update, delete or add

    Returns:
      True if caching is supported for the category and resource.
      False otherwise
    """
        # TODO(dan): Leverage policy manager to apply configured policies
        #
        if self.cache_object.is_caching_supported(category, resource):
            return True
        else:
            return False

    def bulk_get(self, data):
        """Perform Bulk Get operations in cache for specified data.

    Args:
      data: keys for bulk get
    Returns:
     Result of cache get_multi
    """
        return self.cache_object.get_multi(data)

    def bulk_add(self, data, expiration_time=0):
        """Perform Bulk Add operations in cache for specified data.

    Args:
      data: keys for bulk add
    Returns:
     Result of cache add_multi
    """
        return self.cache_object.add_multi(data, expiration_time)

    def bulk_update(self, data, expiration_time=0):
        """Perform Bulk update operations in cache for specified data.

    Does a bulk get on all the items in data and then performs bulk update only
    for items present in cache.

    Args:
      data: keys for bulk update
    Returns:
     Result of cache update_multi
    """
        get_result = self.cache_object.get_multi(data.keys())
        for data_key, data_value in data.items():
            for update_key, update_value in data_value.items():
                if data_key in get_result:
                    get_result[data_key][update_key] = update_value
        return self.cache_object.update_multi(get_result, expiration_time)

    def bulk_delete(self, data, lockadd_seconds):
        """Perform Bulk Delete operations in cache for specified data.

    Args:
      data: keys for bulk delete
    Returns:
     Result of cache remove_multi
    """
        return self.cache_object.remove_multi(data, lockadd_seconds)

    def clean(self):
        """Cleanup cache manager resources."""
        self.cache_object.clean()
        return True

    def clear_cache(self):
        """Clear temporary dictionaries used for cache operations."""
        self.new = {}
        self.dirty = {}
        self.deleted = {}
        self.marked_for_add = {}
        self.marked_for_update = {}
        self.marked_for_delete = []
