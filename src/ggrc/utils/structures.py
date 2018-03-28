# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Collection if ggrc specific structures."""

import collections


class CaseInsensitiveDict(collections.MutableMapping):
    """Case insensitive default dict implementation.

  This is a modification of requests.structures.CaseInsensitiveDict so that it
  works with all types of keys and that it can return a default value when a
  non existing key is accessed.
  """

    def __init__(self, data=None, **kwargs):
        self._store = dict()
        if data is None:
            data = {}
        self.update(data, **kwargs)

    def __getitem__(self, key):
        return self._store[self._key(key)][1]

    def __setitem__(self, key, value):
        """Save the key value pair and remember the actual key."""
        self._store[self._key(key)] = (key, value)

    def __delitem__(self, key):
        del self._store[self._key(key)]

    def __iter__(self):
        return (casedkey for casedkey, mappedvalue in self._store.values())

    def __len__(self):
        return len(self._store)

    def __eq__(self, other):
        """Check if the items in both dicts are the same.

    Case is ignored in comparing keys but not when comparing values.

    Args:
      other: Case insensitive default dict that we want to compare to this one.

    Returns:
      True if all key value pairs match in both dicts where key comparison is
        case insensitive.
    """
        if isinstance(other, collections.Mapping):
            other = CaseInsensitiveDefaultDict(other)
        else:
            return NotImplemented
        # Compare insensitively
        return dict(self.lower_items()) == dict(other.lower_items())

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, dict(self.items()))

    @classmethod
    def _key(cls, key):
        return key.lower() if isinstance(key, basestring) else key

    def lower_items(self):
        """Get items where all keys are lower case."""
        return ((lowerkey, keyval[1])
                for lowerkey, keyval in self._store.items())

    def copy(self):
        return CaseInsensitiveDefaultDict(
            self._default, data=self._store.values())


class CaseInsensitiveDefaultDict(CaseInsensitiveDict):
    """Case insensitive default dict implementation.

  This is a modification of requests.structures.CaseInsensitiveDict so that it
  works with all types of keys and that it can return a default value when a
  non existing key is accessed.
  """

    def __init__(self, _default, data=None, **kwargs):
        self._default = _default
        super(CaseInsensitiveDefaultDict, self).__init__(data, **kwargs)

    def __missing__(self, key):
        """Set a new missing value and return it."""
        if self._default:
            self._store[self._key(key)] = (key, self._default())
            return self._store[self._key(key)][1]
        else:
            raise KeyError(key)

    def __getitem__(self, key):
        """Get an item if it exists or return the default specified value."""
        try:
            return self._store[self._key(key)][1]
        except KeyError:
            return self.__missing__(key)

    def __contains__(self, key):
        return self._key(key) in self._store

    def copy(self):
        return CaseInsensitiveDefaultDict(
            self._default, data=self._store.values())
