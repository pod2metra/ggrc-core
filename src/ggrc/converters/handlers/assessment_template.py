# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Handlers for special object mappings."""

from sqlalchemy.orm.session import make_transient

from ggrc import db
from ggrc import models
from ggrc.converters.handlers import handlers
from ggrc.converters import errors


class AssessmentTemplateColumnHandler(handlers.MappingColumnHandler):
    def parse_item(self):
        if len(self.raw_value.splitlines()) > 1:
            self.add_error(
                errors.WRONG_VALUE_ERROR, column_name=self.display_name)
            return
        if self.raw_value in self.new_slugs:
            self.add_error(
                errors.UNSUPPORTED_OPERATION_ERROR,
                operation="Creating "
                "and using assessment templates in one sheet")
            return
        return super(AssessmentTemplateColumnHandler, self).parse_item()

    def set_obj_attr(self):
        self.value = self.parse_item()
        if not self.dry_run:
            self.create_custom_attributes()

    def insert_object(self):
        pass

    def create_custom_attributes(self):
        table_singular = self.row_converter.obj._inflector.table_singular
        db.session.flush()
        if not self.value:
            return
        template = self.value[0]
        cad = models.CustomAttributeDefinition
        custom_attributes = cad.eager_query().filter(
            cad.definition_type == template._inflector.table_singular,
            cad.definition_id == template.id)
        for attribute_definition in custom_attributes:
            make_transient(attribute_definition)
            attribute_definition.id = None
            attribute_definition.definition_type = table_singular
            attribute_definition.definition_id = self.row_converter.obj.id
            db.session.add(attribute_definition)
        db.session.commit()

    def get_value(self):
        return ""
