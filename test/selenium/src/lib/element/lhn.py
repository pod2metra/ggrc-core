# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""LHN elements."""
# pylint: disable=not-callable
# pylint: disable=not-an-iterable

from selenium.common import exceptions as selenium_exception

from lib import base, exception
from lib.constants import locator
from lib.page import extended_info
from lib.utils import selenium_utils


class _Tab(base.Tab):
    """Tab element."""
    locator_element = None

    def __init__(self, driver):
        """
    Args: driver (base.CustomDriver
    """
        super(_Tab, self).__init__(driver, self.locator_element)


class MyObjectsTab(_Tab):
    """In LHN my objects tab."""
    locator_element = locator.LhnMenu.MY_OBJECTS


class AllObjectsTab(_Tab):
    """In LHN all objects tab."""
    locator_element = locator.LhnMenu.ALL_OBJECTS


class Toggle(base.Toggle):
    """Button in LHN."""

    def __init__(self, driver, locator_element, locator_count):
        super(Toggle, self).__init__(driver, locator_element)
        count_element = selenium_utils.get_when_visible(driver, locator_count)
        self.members_count = int(count_element.text)


class DropdownStatic(base.Dropdown):
    """Dropdown in LHN."""
    _locator_element = None

    def __init__(self, driver):
        super(DropdownStatic, self).__init__(driver, self._locator_element)


class AccordionGroup(base.DropdownDynamic):
    """Mmodel for LHN's accoridon group."""
    _locator_spinny = None
    _locator_button_create_new = None
    _locator_accordion_members = None
    # modal class which is used when creating a new object
    _create_new_modal_cls = None

    def __init__(self, driver):
        """
    Args: driver (base.CustomDriver)
    """
        super(AccordionGroup, self).__init__(
            driver, [self._locator_spinny], wait_until_visible=False)
        self.button_create_new = base.Button(self._driver,
                                             self._locator_button_create_new)
        self._update_loaded_members()
        self._set_visible_members()

    def _update_loaded_members(self):
        self.members_loaded = self._driver.find_elements(
            *self._locator_accordion_members)

    def _set_visible_members(self):
        try:
            for element in self.members_loaded:
                selenium_utils.wait_until_stops_moving(element)
            self.members_visible = [
                element for element in self.members_loaded
                if element.is_displayed()
            ]
        except selenium_exception.StaleElementReferenceException:
            self._update_loaded_members()
            self._set_visible_members()

    def _get_visible_member_by_title(self, member_title):
        """Hovers over visible member with (unique) title "member_title".
    Args: member_title (basestring): (unique) title of member
    Return: selenium.webdriver.remote.webelement.WebElement
    """
        try:
            for element in self.members_visible:
                if element.text == member_title:
                    break
            else:
                raise exception.ElementNotFound
            return element
        except selenium_exception.StaleElementReferenceException:
            # the elements can go stale, here we refresh them
            self._update_loaded_members()
            self._set_visible_members()
            return self._get_visible_member_by_title(member_title)

    def scroll_down(self):
        pass

    def scroll_up(self):
        pass

    def create_new(self):
        """Create new modal for object in LHN.
    Return: lib.page.modal.create_new_object.CreateNewObjectModal
    """
        self.button_create_new.click()
        return self._create_new_modal_cls(self._driver)

    def hover_over_visible_member(self, member_title):
        """Hovers over visible member with (unique) title "member_title".
    Args: member_title (basestring): (unique) title of member
    """
        try:
            el = self._get_visible_member_by_title(member_title)
            selenium_utils.hover_over_element(self._driver, el)
            selenium_utils.get_when_visible(self._driver,
                                            locator.LhnMenu.EXTENDED_INFO)
            return extended_info.ExtendedInfo(self._driver)
        except selenium_exception.StaleElementReferenceException:
            return self.hover_over_visible_member(member_title)
