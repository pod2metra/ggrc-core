# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Base Descriptor.

The module provides base class :class:`Descriptor` to build concrete descriptor
classes.

Descriptor class behaves like a registry for describing objects:

..  code-block:: pycon

    >>> o1 = object()
    >>> o2 = object()
    >>> Descriptor(o1) is Descriptor(o1)
    True
    >>> o1 in Descriptor
    True
    >>> o2 in Descriptor
    False

Derived class should implement :meth:`Descriptor.collect` that should return
an iterator over all objects that have to be wrapped by current descriptor
class.

..  code-block:: pycon

    >>> class Model(Descriptor):
    >>> @classmethod
    >>> def collect(cls):
    >>>   from ggrc.models.all_models import all_models
    >>>   return all_models

Class method :meth:`Descriptor.all` automatically collects objects, sort them
alphabetically and returns their iterator.

By default, described object should have ``__name__`` attribute to be sorted.
If target object doesn't have ``__name__`` attribute, descriptor class should
override :meth:`name`.  Use ``cached_property`` decorator in such cases.

"""

from inspect import getdoc
from collections import OrderedDict

from cached_property import cached_property


class DescriptorMeta(type):
    """Descriptor Metaclass."""

    def __init__(cls, name, bases, attrs):
        """Intializes new descriptor class adding class level registry."""
        cls.__registry__ = OrderedDict()
        cls.__registry__.sorted = False
        cls.__registry__.collected = False
        super(DescriptorMeta, cls).__init__(name, bases, attrs)

    def __contains__(cls, obj):
        """Adds support of ``in`` operation to the class object itself."""
        return id(obj) in cls.__registry__


class Descriptor(object):
    """Base class for concrete descriptor classes."""

    __metaclass__ = DescriptorMeta

    def __new__(cls, obj):
        """Prevents creation of duplicating descriptors for single object."""
        oid = id(obj)
        if oid not in cls.__registry__:
            cls.__registry__[oid] = super(Descriptor, cls).__new__(cls, obj)
            cls.__registry__.sorted = False
        return cls.__registry__[oid]

    @classmethod
    def collect(cls):
        """
    Returns objects that have to be wrapped by the current descriptor.

    The method should be implemented by concrete descriptor class.
    Or method :meth:`all` will not work otherwise.

    """
        raise NotImplementedError('Method should be implemented by subclass')

    @classmethod
    def all(cls):
        """
    Returns iterator over all instances of the class.

    The method uses :meth:`collect` to gather all objects that
    have to be described.  Instances are returned in alphabetical order
    sorted by name.

    """
        if not cls.__registry__.collected:
            for obj in cls.collect():
                cls(obj)
            cls.__registry__.collected = True
        if not cls.__registry__.sorted:
            instances = cls.__registry__.items()
            instances.sort(key=lambda item: item[1].name)
            cls.__registry__.clear()
            cls.__registry__.update(instances)
            cls.__registry__.sorted = True
        return cls.__registry__.itervalues()

    def __init__(self, obj):
        self.obj = obj

    @cached_property
    def name(self):
        """Returns fully qualified described object name."""
        try:
            return '%s.%s' % (self.obj.__module__, self.obj.__name__)
        except AttributeError:
            return self.obj.__name__

    @cached_property
    def doc(self):
        """Returns unindented doc-string of described object."""
        return getdoc(self.obj)
