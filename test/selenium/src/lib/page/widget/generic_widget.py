# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Widgets other than Info widget."""

import re

from selenium.common import exceptions
from selenium.webdriver.common.by import By

from lib import base
from lib.constants import locator, regex, element
from lib.page.modal import base as modal_base
from lib.page.modal.create_new_object import (
    AssessmentTemplatesCreate, AssessmentsCreate, AssessmentsGenerate)
from lib.page.widget import info_widget
from lib.utils import selenium_utils


class Widget(base.Widget):
  """All widgets with filters that list objects and contain describes other
 generic widget components and links to another classes."""
  info_widget_cls = None
  _locator_widget = None
  _locator_filter = None
  members_listed = None
  _locator_generic = locator.BaseWidgetGeneric

  URL_INFO = "{obj_url}" + _locator_generic.widget_info

  def __init__(self, driver):
    self.member_count = None
    self.cls_without_state_filtering = (AssessmentTemplates, )
    # Persons, Workflows, TaskGroups, Cycles, CycleTaskGroupObjectTasks
    self.common_filter_locators = dict(
        text_box_locator=self._locator_filter.TEXTFIELD_TO_FILTER,
        bt_submit_locator=self._locator_filter.BUTTON_FILTER,
        bt_clear_locator=self._locator_filter.BUTTON_RESET)
    self.button_help = base.Button(driver, self._locator_filter.BUTTON_HELP)
    self.filter = base.FilterCommon(driver, **self.common_filter_locators)
    if self.__class__ not in self.cls_without_state_filtering:
      self.dropdown_states = base.DropdownStatic(
          driver, dropdown_locator=self._locator_filter.DROPDOWN,
          elements_locator=self._locator_filter.DROPDOWN_STATES)
    super(Widget, self).__init__(driver)
    self._set_members_listed()

  def _set_member_count(self):
    """Parses widget name and number of items from widget tab title."""
    widget_label = selenium_utils.get_when_visible(
        self._driver, self._locator_widget).text
    # The widget label has 2 forms: "widget_name_plural (number_of_items)"
    # and "number_of_items" and they change depending on how many widgets
    # are open. In order to handle both forms, we first try to parse the
    # first form and only then the second one.
    parsed_label = re.match(regex.WIDGET_TITLE_AND_COUNT, widget_label)
    item_count = (
        widget_label if parsed_label is None else parsed_label.group(2))
    self.member_count = int(item_count)

  def _set_members_listed(self):
    """Wait for listed members to loaded and add them to local container."""
    self._set_member_count()
    if self.member_count:
      # wait until the elements are loaded
      selenium_utils.get_when_invisible(
          self._driver, locator.ObjectWidget.LOADING)
      self.members_listed = self._driver.find_elements(
          *locator.ObjectWidget.MEMBERS_TITLE_LIST)
    else:
      self.members_listed = []

  def wait_for_counter_loaded(self):
    """Wait for elements' counter on Filter panel to be visible."""
    return selenium_utils.get_when_visible(
        self._driver, locator.BaseWidgetGeneric.FILTER_PANE_COUNTER)

  def verify_counter_not_loaded(self):
    """Check that in case of empty table, counter not loaded on filter panel.
    """
    selenium_utils.wait_for_element_text(
        self._driver,
        locator.BaseWidgetGeneric.FILTER_PANE_COUNTER, "No records")

  def get_items_count(self):
    """Get elements' count from counter on filter panel."""
    return self.wait_for_counter_loaded().text.split()[2]

  def wait_member_deleted(self, count):
    """Wait until elements' counter on filter panel refreshed with new value.
    Args: count (str)
    """
    if count != '1':
      new_count = ' {} '.format(int(count) - 1)
      selenium_utils.wait_for_element_text(
          self._driver, locator.BaseWidgetGeneric.FILTER_PANE_COUNTER,
          new_count)
    else:
      self.verify_counter_not_loaded()

  def select_member_by_num(self, num):
    """Select member from list of members by number (start from 0).
    Args: num (int)
    Return: lib.page.widget.info.Widget
    """
    # pylint: disable=not-callable
    try:
      member = self.members_listed[num]
      # wait for the listed items animation to stop
      selenium_utils.wait_until_stops_moving(member)
      member.click()
      # wait for the info pane animation to stop
      info_pane = selenium_utils.get_when_clickable(
          self._driver, locator.ObjectWidget.INFO_PANE)
      selenium_utils.wait_until_stops_moving(info_pane)
      return self.info_widget_cls(self._driver)
    except exceptions.StaleElementReferenceException:
      self.members_listed = self._driver.find_elements(
          *locator.ObjectWidget.MEMBERS_TITLE_LIST)
      return self.select_member_by_num(num)
    except exceptions.TimeoutException:
      # sometimes the click to the listed member results in hover
      return self.select_member_by_num(num)


class TreeView(base.TreeView):
  """Genetic Tree Views."""
  _locators = locator.TreeView

  def __init__(self, driver, widget_name):
    """
    Args: driver (CustomDriver), widget_name (#widget_name according URL)
    """
    super(TreeView, self).__init__(driver, widget_name)
    self.widget_name = widget_name
    self.button_create = None
    self.button_3bbs = None
    self.button_generate = None
    self.button_show_fields = None
    self.visible_fields = modal_base.SetFieldsModal(
        driver, widget_name=self.widget_name)

  @staticmethod
  def wait_loading_after_actions(driver):
    """Wait loading elements of Tree View after made some action with
    object(s) under Tree View.
    """
    selenium_utils.wait_until_not_present(
        driver, locator.TreeView.ITEM_LOADING)
    selenium_utils.get_when_invisible(driver, locator.TreeView.SPINNER)

  def open_create_obj(self):
    """Open modal from Tree View to create new object."""
    _locator_create = (
        By.CSS_SELECTOR,
        self._locators.BUTTON_3BBS_CREATE.format(self.widget_name))
    self.button_create = base.Button(self._driver, _locator_create)
    self.button_create.click()

  def open_tree_view_3bbs(self):
    """Click to 3BBS button on Tree View to open modal for further actions.
    """
    _locator_3bbs = (
        By.CSS_SELECTOR, self._locators.BUTTON_3BBS.format(self.widget_name))
    self.button_3bbs = base.Button(self._driver, _locator_3bbs)
    self.button_3bbs.click()

  def select_generate_objs(self):
    """Open modal previously clicked to 3BBS button from Tree View to generate
    new object(s).
    """
    self.open_tree_view_3bbs()
    _locator_generate = (
        By.CSS_SELECTOR,
        self._locators.BUTTON_3BBS_GENERATE.format(self.widget_name))
    self.button_generate = base.Button(self._driver, _locator_generate)
    self.button_generate.click()

  def select_set_fields(self):
    """Open modal previously clicked to 'Show fields' button from Tree View to
    set visible fields for represent Tree View objects.
    """
    _locator_show_fields = (
        By.CSS_SELECTOR,
        self._locators.BUTTON_SHOW_FIELDS.format(self.widget_name))
    self.button_show_fields = base.Button(self._driver, _locator_show_fields)
    self.button_show_fields.click()

  def create_obj(self, new_obj):
    """Create new object from widget used Tree View."""
    self.open_create_obj()
    return new_obj(self._driver)

  def generate_objs(self, new_obj):
    """Generate new object(s) from widget used Tree View."""
    self.select_generate_objs()
    return new_obj(self._driver)

  def set_visible_fields_for_objs(self, fields):
    """Set and save visible fields to display objects on Tree View."""
    self.select_set_fields()
    self.visible_fields.set_and_save_visible_fields(fields)

  def get_objs_as_list_dicts(self, fields):
    """Get list of dicts from objects (text scopes) which displayed on
    Tree View on widget according to set of visible fields.
    """
    list_headers = [_item.text.splitlines()[:len(fields)] for
                    _item in self.tree_view_header_elements()]
    list_lists_items = [_item.text.splitlines()[:len(fields)] for
                        _item in self.tree_view_items_elements()]
    return [dict(zip(list_headers[0], item)) for item in list_lists_items]

  def select_member_by_title(self, title):
    """Select member in Tree View by member's title."""
    item = [_item for _item in self.tree_view_items_elements() if
            title in _item.text.splitlines()][0]
    selenium_utils.wait_until_stops_moving(item)
    item.click()


class Audits(Widget):
  """Model for Audits generic widgets."""
  info_widget_cls = info_widget.AuditsInfoWidget
  _locator_widget = locator.WidgetBar.AUDITS
  _locator_filter = locator.WidgetAudits

  URL = "{source_obj_url}" + _locator_filter.widget_name

  def __init__(self, driver):
    super(Audits, self).__init__(driver)
    self.tree_view = TreeView(
        driver, widget_name=self._locator_filter.widget_name)


class AssessmentTemplates(Widget):
  """Model for Assessment Templates generic widgets."""
  info_widget_cls = info_widget.AssessmentTemplatesInfoWidget
  _locator_widget = locator.WidgetBar.ASSESSMENT_TEMPLATES
  _locator_filter = locator.WidgetAssessmentTemplates
  _asmt_tmpls_fields = (
      element.AssessmentTemplateModalSetVisibleFields.DEFAULT_SET_FIELDS)

  URL = "{source_obj_url}" + _locator_filter.widget_name

  def __init__(self, driver):
    super(AssessmentTemplates, self).__init__(driver)
    self.tree_view = TreeView(
        driver, widget_name=self._locator_filter.widget_name)

  def create(self):
    """Create Assessment Template from widget."""
    return self.tree_view.create_obj(AssessmentTemplatesCreate)

  def set_visible_fields(self):
    """Set visible fields for display Assessment Templates on Tree View."""
    self.tree_view.set_visible_fields_for_objs(self._asmt_tmpls_fields)

  def get_list_objs_scopes(self):
    """Get list of Assessment Templates scopes which displayed on Tree View."""
    self.set_visible_fields()
    return self.tree_view.get_objs_as_list_dicts(self._asmt_tmpls_fields)


class Assessments(Widget):
  """Model for Assessments generic widgets."""
  info_widget_cls = info_widget.AssessmentsInfoWidget
  _locator_widget = locator.WidgetBar.ASSESSMENTS
  _locator_filter = locator.WidgetAssessments
  _asmts_fields = element.AssessmentModalSetVisibleFields.DEFAULT_SET_FIELDS

  URL = "{source_obj_url}" + _locator_filter.widget_name

  def __init__(self, driver):
    super(Assessments, self).__init__(driver)
    self.tree_view = TreeView(
        driver, widget_name=self._locator_filter.widget_name)

  def create(self):
    """Create Assessment from widget."""
    return self.tree_view.create_obj(AssessmentsCreate)

  def generate(self):
    """Generate Assessment(s) from widget."""
    return self.tree_view.generate_objs(AssessmentsGenerate)

  def set_visible_fields(self):
    """Set visible fields for display Assessments on Tree View."""
    self.tree_view.set_visible_fields_for_objs(self._asmts_fields)

  def get_list_objs_scopes(self):
    """Get list of Assessments scopes which displayed on Tree View."""
    self.set_visible_fields()
    return self.tree_view.get_objs_as_list_dicts(self._asmts_fields)


class Controls(Widget):
  """Model for Controls generic widgets."""
  info_widget_cls = info_widget.ControlsInfoWidget
  _locator_widget = locator.WidgetBar.CONTROLS
  _locator_filter = locator.WidgetControls
  _controls_fields = element.ControlModalSetVisibleFields().DEFAULT_SET_FIELDS

  URL = "{source_obj_url}" + _locator_filter.widget_name

  def __init__(self, driver,):
    super(Controls, self).__init__(driver)
    self.tree_view = TreeView(
        driver, widget_name=self._locator_filter.widget_name)

  def update_ver(self, obj_title):
    """Update version of Control via Info panel from Tree View."""
    self.tree_view.select_member_by_title(obj_title)
    info_panel = self.info_widget_cls(self._driver)
    info_panel.open_link_get_latest_ver().confirm_update()
    self.tree_view.wait_loading_after_actions(self._driver)
    selenium_utils.get_when_invisible(
        self._driver, locator.CommonWidgetInfoSnapshots.LINK_GET_LAST_VER)

  def is_editable(self, obj_title):
    """Check Control is editable via Info panel from Tree View."""
    self.tree_view.select_member_by_title(obj_title)
    info_panel = self.info_widget_cls(self._driver)
    return info_panel.open_info_3bbs().is_edit_exist()

  def is_openable(self, obj_title):
    """Check Control is openable via Info panel from Tree View."""
    self.tree_view.select_member_by_title(obj_title)
    info_panel = self.info_widget_cls(self._driver)
    return info_panel.open_info_3bbs().is_open_exist()

  def is_updateble(self, obj_title):
    """Check Control is updateble via Info panel from Tree View."""
    self.tree_view.select_member_by_title(obj_title)
    info_panel = self.info_widget_cls(self._driver)
    return info_panel.is_link_get_latest_ver_exist()

  def set_visible_fields(self):
    """Set visible fields for display Controls on Tree View."""
    self.tree_view.set_visible_fields_for_objs(self._controls_fields)

  def get_list_objs_scopes(self):
    """Get list of Controls scopes which displayed on Tree view."""
    self.set_visible_fields()
    return self.tree_view.get_objs_as_list_dicts(self._controls_fields)


class Issues(Widget):
  """Model for Issues generic widgets"""
  info_widget_cls = info_widget.IssuesInfoWidget
  _locator_widget = locator.WidgetBar.ISSUES
  _locator_filter = locator.WidgetIssues
  _issues_fields = element.IssueModalSetVisibleFields.DEFAULT_SET_FIELDS

  URL = "{source_obj_url}" + _locator_filter.widget_name

  def __init__(self, driver):
    super(Issues, self).__init__(driver)
    self.tree_view = TreeView(
        driver, widget_name=self._locator_filter.widget_name)

  def set_visible_fields(self):
    """Set visible fields for display Issues on Tree View."""
    self.tree_view.set_visible_fields_for_objs(self._issues_fields)

  def get_list_objs_scopes(self):
    """Get list of Issues scopes which displayed on Tree View."""
    self.set_visible_fields()
    return self.tree_view.get_objs_as_list_dicts(self._issues_fields)


class Programs(Widget):
  """Model for Programs generic widgets"""
  info_widget_cls = info_widget.ProgramsInfoWidget
  _locator_widget = locator.WidgetBar.PROGRAMS
  _locator_filter = locator.WidgetPrograms
  _programs_fields = element.ProgramModalSetVisibleFields.DEFAULT_SET_FIELDS

  URL = "{source_obj_url}" + _locator_filter.widget_name

  def __init__(self, driver):
    super(Programs, self).__init__(driver)
    self.tree_view = TreeView(driver,
                              widget_name=self._locator_filter.widget_name)

  def set_visible_fields(self):
    """Set visible fields for display Programs on Tree View."""
    self.tree_view.set_visible_fields_for_objs(self._programs_fields)

  def get_list_objs_scopes(self):
    """Get list of Programs scopes which displayed on Tree View."""
    self.set_visible_fields()
    return self.tree_view.get_objs_as_list_dicts(self._programs_fields)


class Processes(Widget):
  """Model for Process generic widgets."""
  info_widget_cls = info_widget.ProcessesInfoWidget
  _locator_widget = locator.WidgetBar.PROCESSES
  _locator_filter = locator.WidgetProcesses


class DataAssets(Widget):
  """Model for Data Assets generic widgets."""
  info_widget_cls = info_widget.DataAssetsInfoWidget
  _locator_widget = locator.WidgetBar.DATA_ASSETS
  _locator_filter = locator.WidgetDataAssets


class Systems(Widget):
  """Model for Systems generic widgets."""
  info_widget_cls = info_widget.SystemsInfoWidget
  _locator_widget = locator.WidgetBar.SYSTEMS
  _locator_filter = locator.WidgetSystems


class Products(Widget):
  """Model for Products generic widgets."""
  info_widget_cls = info_widget.ProductsInfoWidget
  _locator_widget = locator.WidgetBar.PRODUCTS
  _locator_filter = locator.WidgetProducts


class Projects(Widget):
  """Model for Projects generic widgets."""
  info_widget_cls = info_widget.ProjectsInfoWidget
  _locator_widget = locator.WidgetBar.PROJECTS
  _locator_filter = locator.WidgetProjects
