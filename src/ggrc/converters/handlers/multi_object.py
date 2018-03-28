# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Handlers for special object mappings."""

from ggrc.converters import errors
from ggrc.converters import get_importables
from ggrc.converters.handlers import handlers


class ObjectsColumnHandler(handlers.ColumnHandler):
    def __init__(self, row_converter, key, **options):
        self.mappable = get_importables()
        self.new_slugs = row_converter.block_converter.converter.new_objects
        super(ObjectsColumnHandler, self).__init__(row_converter, key,
                                                   **options)

    def parse_item(self):
        lines = [line.split(":", 1) for line in self.raw_value.splitlines()]
        objects = []
        for line in lines:
            if len(line) != 2:
                self.add_warning(
                    errors.WRONG_VALUE, column_name=self.display_name)
                continue
            object_class, slug = line
            slug = slug.strip()
            class_ = self.mappable.get(object_class.strip().lower())
            if class_ is None:
                self.add_warning(
                    errors.WRONG_VALUE, column_name=self.display_name)
                continue
            new_object_slugs = self.new_slugs[class_]
            obj = class_.query.filter(class_.slug == slug).first()
            if obj:
                objects.append(obj)
            elif not (slug in new_object_slugs and self.dry_run):
                self.add_warning(
                    errors.UNKNOWN_OBJECT,
                    object_type=class_._inflector.human_singular.title(),
                    slug=slug)
        return objects

    def set_obj_attr(self):
        self.value = self.parse_item()

    def get_value(self):
        return ""

    def insert_object(self):
        pass

    def set_value(self):
        """This should be ignored with second class attributes."""
