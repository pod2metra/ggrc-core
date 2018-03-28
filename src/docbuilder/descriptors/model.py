# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Model related descriptors."""

from cached_property import cached_property
from sqlalchemy.dialects import mysql
from sqlalchemy.schema import CreateTable

from docbuilder.descriptors.base import Descriptor


class Model(Descriptor):
    """Model class descriptor."""

    @classmethod
    def collect(cls):
        """Collects all model classes."""
        from ggrc.models.all_models import all_models

        return all_models

    @cached_property
    def mixins(self):
        """List of mixins used by the target model."""
        return [
            Mixin(class_) for class_ in self.obj.__mro__[1:]
            if class_.__module__.startswith('ggrc')
        ]

    @cached_property
    def create_table(self):
        """Text of "CREATE TABLE ..." query."""
        # pylint: disable=no-value-for-parameter
        query = CreateTable(
            self.obj.__table__).compile(dialect=mysql.dialect())
        return str(query).strip()


class Mixin(Descriptor):
    """Model mixin class descriptor."""

    @classmethod
    def collect(cls):
        """Collects all mixin classes."""
        result = set()
        for model in Model.all():
            result.update(m.obj for m in model.mixins)
        return result
