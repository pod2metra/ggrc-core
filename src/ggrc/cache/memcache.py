# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

from google.appengine.api import memcache
from cache import Cache
from cache import all_cache_entries
from collections import OrderedDict
from copy import deepcopy
"""
    Memcache implements the remote AppEngine Memcache mechanism

"""


class MemCache(Cache):
    def __init__(self):
        self.name = 'memcache'
        self.client = None

        for cache_entry in all_cache_entries():
            if cache_entry.cache_type is self.name:
                self.supported_resources[
                    cache_entry.model_plural] = cache_entry.class_name
                self.memcache_client = memcache.Client()

    def get_name(self):
        return self.name

    def get(self, category, resource, filter):
        """ get items from mem cache for specified filter

    Args:
      category: collection or stub
      resource: regulation, controls, etc.
      filter: dictionary containing ids and optional attrs

    Returns:
      All or None policy is applied by default
      None on any errors
      otherwise returns JSON string representation
    """

        if not self.is_caching_supported(category, resource):
            return None
        # TODO(dan): use memcache.Client.get_multi() instead of gets()
        #
        data = OrderedDict()
        cache_key = self.get_key(category, resource)
        if cache_key is None:
            return None
        ids, attrs = self.parse_filter(filter)
        if ids is None and attrs is None:
            return None
        else:
            if ids is None:
                return None
        for id in ids:
            attrvalues = self.memcache_client.gets(cache_key + ":" + str(id))
            if attrvalues is not None:
                if attrs is None:
                    data[id] = attrvalues
                else:
                    attr_dict = OrderedDict()
                    for attr in attrs:
                        if attrvalues.has_key(attr):
                            attr_dict[attr] = deepcopy(attrvalues.get(attr))
                    data[id] = attr_dict
            else:
                # All or None policy is enforced, if one of the objects is not available in cache, then we return empty
                # TODO(dan): cannot distinguish network failures vs id not found in memcache, both scenarios return empty list
                return None
        return data

    def add(self, category, resource, data, expiration_time=0):
        """ add data to mem cache

    Args:
      category: collection or stub
      resource: regulation, controls, etc.
      data: dictionary containing ids and attrs

    Returns:
      None on any errors
      Mapping of DTO formatted string, e.g. JSON string representation
    """
        if not self.is_caching_supported(category, resource):
            return None
        entries = {}
        cache_key = self.get_key(category, resource)
        if cache_key is None:
            return None
        # TODO(dan): use memcache.Client.add_multi() instead of add()
        for key in data.keys():
            id = cache_key + ":" + str(key)
            cache_data = self.memcache_client.gets(id)
            if cache_data is None:
                if self.memcache_client.add(id, data.get(key),
                                            expiration_time) is False:
                    # We stop processing any further
                    # TODO(ggrcdev): Should we throw exceptions and/or log critical events
                    return None
                else:
                    entries[key] = data
            else:
                # This could occur on import scenarios
                #
                if self.memcache_client.cas(id, data.get(key),
                                            expiration_time) is False:
                    # We stop processing any further
                    # TODO(ggrcdev): Should we throw exceptions and/or log critical events
                    return None
                else:
                    entries[key] = data
        return entries

    def update(self, category, resource, data, expiration_time):
        """ Update items from mem cache for specified data

    Args:
      category: collection or stub
      resource: regulation, controls, etc.
      filter: dictionary containing ids and attrs

    Returns:
      None on any errors
      Mapping of DTO formatted string, e.g. JSON string representation
    """
        if not self.is_caching_supported(category, resource):
            return None
        entries = {}
        cache_key = self.get_key(category, resource)
        if cache_key is None:
            return None
        # TODO(ggrcdev): use memcache.Client.cas_multi(), get_multi() instead of cas(), gets()
        #
        for key in data.keys():
            id = cache_key + ":" + str(key)
            if self.memcache_client.cas(id, data.get(key),
                                        expiration_time) is False:
                # RPC Error or value is not id is not found in cache.
                # Cannot proceed further with update (All or None) policy
                return None
            else:
                entries[key] = data
        return entries

    def remove(self, category, resource, data, lockadd_seconds=0):
        """ delete items from mem cache for specified data

    Args:
      category: collection or stub
      resource: regulation, controls, etc.
      data: List of keys

    Returns:
      None on any errors
      mapping of DTO formatted string, e.g. JSON string representation
    """
        if not self.is_caching_supported(category, resource):
            return None
        entries = {}
        cache_key = self.get_key(category, resource)
        if cache_key is None:
            return None
        # TODO(dan): use memcache.Client.delete_multi(), get_multi() instead of delete(), gets()
        #
        for key in data.keys():
            id = cache_key + ":" + str(key)
            retvalue = self.memcache_client.delete(id, lockadd_seconds)
            # Log the event of delete failures
            if retvalue is 0:
                # retvalue of 0 indicates Network failure, Cannot proceed further with delete (All or None) policy
                return None
            elif retvalue is 2:
                # retvalue of 2 indicates Success
                entries[key] = data
            elif retvalue is 1:
                # retvalue of 1 indicates id is not present in memcache (could be expired), proceed with next entry
                continue
            else:
                # Any other return value, Cannot proceed further with delete (All or None) policy
                #
                return None
        return entries

    def add_multi(self, data, expiration_time=0):
        """ Add multiple entries to memcache
    There are limits to size of data in memcache

    Args:
      category: collection or stub
      resource: regulation, controls, etc.
      data: dictionary containing ids and dictionary of attrs

    Returns:
      memcache client API add_multi
    """
        # TODO(dan): import scenarios, add will return non-empty list, we should invoke update_multi for those items
        #
        return self.memcache_client.add_multi(data, expiration_time)

    def get_multi(self, data):
        """ Get multiple entries from memcache
    There are limits to size of data in memcache

    Args:
      category: collection or stub
      resource: regulation, controls, etc.
      data: dictionary containing ids

    Returns:
      memcache client API get_multi
    """
        return self.memcache_client.get_multi(data, '', None, True)

    def update_multi(self, data, expiration_time=0):
        """ update multiple entries to memcache
    There are limits to size of data in memcache

    Args:
      category: collection or stub
      resource: regulation, controls, etc.
      data: dictionary containing ids and dictionary of attrs

    Returns:
      memcache client API cas_multi (compare and set)
    """
        return self.memcache_client.cas_multi(data, expiration_time)

    def remove_multi(self, data, lockadd_seconds):
        """ delete multiple entries to memcache

    Args:
      category: collection or stub
      resource: regulation, controls, etc.
      data:  list of keys

    Returns:
      memcache client API delete_multi
    """
        return self.memcache_client.delete_multi(data, lockadd_seconds)

    def clean(self):
        """ flush everything from memcache """
        return self.memcache_client.flush_all()
