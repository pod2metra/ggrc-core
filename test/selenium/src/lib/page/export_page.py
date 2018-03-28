# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Export page with Export Panels."""

from datetime import datetime

from lib import base
from lib.constants import locator, element
from lib.utils import selenium_utils


class ExportPanel(base.Component):
    """Export Panel on Export Page."""

    def __init__(self, driver, export_panel):
        super(ExportPanel, self).__init__(driver)


class ExportPage(base.Page):
    """Export Page."""
    _locators = locator.ExportPage
    _elements = element.ExportPage

    def __init__(self, driver):
        super(ExportPage, self).__init__(driver)
        self.export_page = self._driver.find_element(
            *self._locators.EXPORT_PAGE_CSS)
        self.export_panels = self.get_list_export_panels()
        self.add_obj_type_btn = base.Button(
            self.export_page, self._locators.ADD_OBJECT_TYPE_BTN_XPATH)
        self.export_actions_panel = self.export_page.find_element(
            *self._locators.EXPORT_ACTIONS_PANEL_CSS)
        self.export_format_dd = base.DropdownStatic(
            self.export_actions_panel, self._locators.EXPORT_FORMAT_DD_CSS)
        self.export_objs_btn = base.Button(
            self.export_actions_panel, self._locators.EXPORT_OBJECTS_BTN_CSS)

    def get_list_export_panels(self):
        """Get list of all Export Panels witch are presented on Export Page at the
    moment of getting.
    """
        # pylint: disable=invalid-name
        # reason: to make method's name informative
        return [
            ExportPanel(self._driver, exp_panel_el)
            for exp_panel_el in self.export_page.find_elements(
                *self._locators.EXPORT_PANEL_CSS)
        ]

    def click_export_objs_and_get_datetime(self):
        """Click to 'Export Objects' button to confirm export objects according to
    selected before export format (Google Sheet or CSV) and get datetime of
    the clicking's moment.
    """
        # pylint: disable=invalid-name
        # reason: to make method's name informative
        self.export_objs_btn.click()
        datetime_of_export_clicking = datetime.now()
        selenium_utils.get_when_invisible(self.export_page,
                                          locator.Common.SPINNER_CSS)
        selenium_utils.wait_for_js_to_load(self._driver)
        return datetime_of_export_clicking

    def export_objs_to_csv_and_return_datetime(self):
        """Export objects choosing CSV as exporting format and return datetime of
    export clicking.
    """
        # pylint: disable=invalid-name
        # reason: to make method's name informative
        self.export_format_dd.select_by_label(self._elements.CSV)
        return self.click_export_objs_and_get_datetime()
