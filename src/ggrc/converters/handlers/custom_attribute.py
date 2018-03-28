# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Handlers used for custom attribute columns."""
from datetime import datetime
from dateutil.parser import parse

from sqlalchemy import and_

from ggrc import models
from ggrc import utils
from ggrc.converters import errors
from ggrc.converters.handlers import handlers

_types = models.CustomAttributeDefinition.ValidTypes


def _get_ca_date_value(value):
    """Extract formatted value for ca with date type."""
    try:
        attr_val = datetime.strptime(value.attribute_value,
                                     "%Y-%m-%d").strftime("%m/%d/%Y")
    except ValueError:
        attr_val = u""
    return attr_val


class CustomAttributeColumHandler(handlers.TextColumnHandler):
    """Custom attribute column handler

  This is a handler for all types of custom attribute column. It works with
  any custom attribute definition and with mondatory flag on or off.
  """

    _type_handlers = {
        _types.TEXT: lambda self: self.get_text_value(),
        _types.DATE: lambda self: self.get_date_value(),
        _types.DROPDOWN: lambda self: self.get_dropdown_value(),
        _types.CHECKBOX: lambda self: self.get_checkbox_value(),
        _types.RICH_TEXT: lambda self: self.get_rich_text_value(),
        _types.MAP: lambda self: self.get_person_value(),
    }

    def set_obj_attr(self):
        """Set object attribute method should do nothing for custom attributes.

    CA values set in insert_object() method.
    """
        if self.value is None:
            return

        cav = self._get_or_create_ca()
        cav.attribute_value = self.value
        if isinstance(cav.attribute_value, models.mixins.base.Identifiable):
            obj = cav.attribute_value
            cav.attribute_value = obj.__class__.__name__
            cav.attribute_object_id = obj.id

    def parse_item(self):
        """Parse raw value from csv file

    Returns:
      CustomAttributeValue with the correct definition type and value.
    """
        self.definition = self.get_ca_definition()
        if self.definition is None:
            # In dry run mode CADs is not created for new objects.
            if not self.dry_run:
                self.add_warning(
                    errors.INVALID_ATTRIBUTE_WARNING,
                    column_name=self.display_name)
            return None
        type_ = self.definition.attribute_type.split(":")[0]
        value_handler = self._type_handlers[type_]
        return value_handler(self)

    def get_value(self):
        """Return the value of the custom attrbute field.

    Returns:
      Text representation if the custom attribute value if it exists, otherwise
      None.
    """
        definition = self.get_ca_definition()
        if not definition:
            return ""

        for value in self.row_converter.obj.custom_attribute_values:
            if value.custom_attribute_id == definition.id:
                if value.custom_attribute.attribute_type.startswith("Map:"):
                    if value.attribute_object_id:
                        obj = value.attribute_object
                        return getattr(obj, "email", getattr(
                            obj, "slug", None))
                elif value.custom_attribute.attribute_type == _types.CHECKBOX:
                    attr_val = value.attribute_value if value.attribute_value else u"0"
                    try:
                        attr_val = int(attr_val)
                    except ValueError:
                        attr_val = False
                    return str(bool(attr_val)).upper()
                elif value.custom_attribute.attribute_type == _types.DATE:
                    return _get_ca_date_value(value)
                else:
                    return value.attribute_value

        return None

    def _get_or_create_ca(self):
        """Get a CA value object for the current definition.

    This function returns a custom attribute value object that already existed
    or creates a new one.

    Returns:
        custom attribute value object.
    """
        ca_definition = self.get_ca_definition()
        if not self.row_converter.obj or not ca_definition:
            return None
        for ca_value in self.row_converter.obj.custom_attribute_values:
            if ca_value.custom_attribute_id == ca_definition.id:
                return ca_value
        ca_value = models.CustomAttributeValue(
            custom_attribute=ca_definition,
            attributable=self.row_converter.obj,
        )
        return ca_value

    def insert_object(self):
        """Add custom attribute objects to db session."""

    def get_date_value(self):
        """Get date value from input string date."""
        if not self.mandatory and self.raw_value == "":
            return None  # ignore empty fields
        value = None
        try:
            value = parse(self.raw_value).strftime(utils.DATE_FORMAT_ISO, )
        except (TypeError, ValueError):
            self.add_warning(errors.WRONG_VALUE, column_name=self.display_name)
        if self.mandatory and value is None:
            self.add_error(
                errors.MISSING_VALUE_ERROR, column_name=self.display_name)
        return value

    def get_checkbox_value(self):
        """Get boolean value for checkbox fields."""
        if not self.mandatory and self.raw_value == "":
            return None  # ignore empty fields
        value = self.raw_value.lower() in ("yes", "true")
        if self.raw_value.lower() not in ("yes", "true", "no", "false"):
            self.add_warning(errors.WRONG_VALUE, column_name=self.display_name)
            value = None
        if self.mandatory and value is None:
            self.add_error(
                errors.MISSING_VALUE_ERROR, column_name=self.display_name)
        return value

    def get_dropdown_value(self):
        """Get valid value of the dropdown field."""
        choices_list = self.definition.multi_choice_options.split(",")
        valid_choices = [val.strip() for val in choices_list]
        choice_map = {choice.lower(): choice for choice in valid_choices}
        value = choice_map.get(self.raw_value.lower())
        if value is None and self.raw_value != "":
            self.add_warning(errors.WRONG_VALUE, column_name=self.display_name)
        if self.mandatory and value is None:
            self.add_error(
                errors.MISSING_VALUE_ERROR, column_name=self.display_name)
        return value

    def get_text_value(self):
        if not self.mandatory and self.raw_value == "":
            return None  # ignore empty fields
        value = self.clean_whitespaces(self.raw_value)
        if self.mandatory and not value:
            self.add_error(
                errors.MISSING_VALUE_ERROR, column_name=self.display_name)
        return value

    def get_rich_text_value(self):
        if not self.mandatory and self.raw_value == "":
            return None  # ignore empty fields
        if self.mandatory and not self.raw_value:
            self.add_error(
                errors.MISSING_VALUE_ERROR, column_name=self.display_name)
        return self.raw_value

    def get_person_value(self):
        """Fetch a person based on the email text in column.

    Returns:
        Person model instance
    """
        if not self.mandatory and self.raw_value == "":
            return None  # ignore empty fields
        if self.mandatory and not self.raw_value:
            self.add_error(
                errors.MISSING_VALUE_ERROR, column_name=self.display_name)
            return
        value = models.Person.query.filter_by(email=self.raw_value).first()
        if self.mandatory and not value:
            self.add_error(errors.WRONG_VALUE, column_name=self.display_name)
        return value

    def get_ca_definition(self):
        """Get custom attribute definition."""
        cache = self.row_converter.block_converter.get_ca_definitions_cache()
        return cache.get((None, self.display_name))


class ObjectCaColumnHandler(CustomAttributeColumHandler):
    """Handler for object level custom attributes."""

    def set_value(self):
        pass

    def set_obj_attr(self):
        """Parse item and set the current value.

    This is a hack to get set_value on this handler called after all other
    values have already been set.
    """
        self.value = self.parse_item()
        super(ObjectCaColumnHandler, self).set_obj_attr()

    def get_ca_definition(self):
        """Get custom attribute definition for a specific object."""
        if self.row_converter.obj.id is None:
            return None
        cad = models.CustomAttributeDefinition
        cache = self.row_converter.block_converter.get_ca_definitions_cache()
        definition = cache.get((self.row_converter.obj.id, self.display_name))
        if not definition:
            definition = cad.query.filter(
                and_(cad.definition_id == self.row_converter.obj.id,
                     cad.title == self.display_name)).first()
        return definition
