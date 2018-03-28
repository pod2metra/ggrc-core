# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Descriptors.

The package provides utilities to gather information about core objects
of the GGRC application that have to be documented.

"""

from docbuilder.descriptors.package import Package
from docbuilder.descriptors.service import Service
from docbuilder.descriptors.model import Model, Mixin

__all__ = ['Package', 'Service', 'Model', 'Mixin']
