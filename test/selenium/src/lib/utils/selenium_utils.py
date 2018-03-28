# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Utility functions for selenium."""

import json
import logging
import time

from selenium.common import exceptions
from selenium.webdriver.common import action_chains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from lib import constants, exception
from lib.constants import messages, locator as locators
from lib.constants import value_aliases as alias

LOGGER = logging.getLogger(__name__)


def _webdriver_wait(driver):
    """Common WebDriverWait logic with poll frequency."""
    return WebDriverWait(
        driver,
        constants.ux.MAX_USER_WAIT_SECONDS,
        poll_frequency=constants.ux.POLL_FREQUENCY)


def hover_over_element(driver, element):
    """Move mouse pointer to element and hover."""
    action_chains.ActionChains(driver).move_to_element(element).perform()


def open_url(driver, url, is_via_js=False):
    """Open URL in current browser session, window, tab if this URL hasn't been
  opened yet and wait till the moment when web document will be fully loaded.
  If 'is_via_js' then use JS to perform opening.
  """
    if driver.current_url != url:
        if not is_via_js:
            driver.get(url)
        else:
            driver.execute_script("window.open('{}', '_self')".format(url))
        wait_for_doc_is_ready(driver)


def switch_to_new_window(driver):
    """Wait until new window will be opened, have the number of windows handles
  increase and then switch to last opened window.
  """
    try:
        wait_until_condition(driver, EC.new_window_is_opened)
        driver.switch_to.window(driver.window_handles.pop())
    except:
        raise exceptions.NoSuchWindowException(
            messages.ExceptionsMessages.err_switch_to_new_window)


def wait_until_stops_moving(element):
    """Wait until element stops moving.
 Args: selenium.webdriver.remote.webelement.WebElement
 """
    prev_location = None
    timer_begin = time.time()
    while prev_location != element.location:
        prev_location = element.location
        time.sleep(0.1)
        if time.time() - timer_begin > constants.ux.ELEMENT_MOVING_TIMEOUT:
            raise exception.ElementMovingTimeout


def is_element_exist(driver, locator):
    """
  Args: driver (base.CustomDriver), locator (tuple)
  Return: True if element is exist, False if element is not exist.
  """
    try:
        driver.find_element(*locator)
        return True
    except exceptions.NoSuchElementException:
        return False


def get_when_visible(driver, locator):
    """
 Args: driver (base.CustomDriver), locator (tuple)
 Return: selenium.webdriver.remote.webelement.WebElement
 """
    return (_webdriver_wait(driver).until(
        EC.visibility_of_element_located(locator)))


def wait_until_condition(driver, condition):
    """Wait until given expected condition is met."""
    _webdriver_wait(driver).until(condition)


def wait_until_element_visible(driver, locator):
    """Wait until element for given locator are present in DOM and visible."""
    wait_until_condition(driver, EC.visibility_of_element_located(locator))


def wait_until_not_present(driver, locator):
    """Wait until no element(-s) for locator given are present in DOM."""
    wait_until_condition(driver, lambda d: len(d.find_elements(*locator)) == 0)


def get_when_all_visible(driver, locator):
    """Return elements by locator when all of them are visible.
 Args: driver (base.CustomDriver), locator (tuple)
 Return: selenium.webdriver.remote.webelement.WebElements
 """
    return (_webdriver_wait(driver).until(
        EC.visibility_of_all_elements_located(locator)))


def get_when_clickable(driver, locator):
    """
 Args: driver (base.CustomDriver), locator (tuple)
 Return: selenium.webdriver.remote.webelement.WebElement
 """
    return (_webdriver_wait(driver).until(EC.element_to_be_clickable(locator)))


def get_when_invisible(driver, locator):
    """
 Args: driver (base.CustomDriver), locator (tuple)
 Return: selenium.webdriver.remote.webelement.WebElement
 """
    return (_webdriver_wait(driver).until(
        EC.invisibility_of_element_located(locator)))


def wait_for_element_text(driver, locator, text):
    """
    Args: driver (base.CustomDriver), locator (tuple), text (str)
 """
    return (_webdriver_wait(driver).until(
        EC.text_to_be_present_in_element(locator, text)))


def is_value_in_attr(element, attr="class", value="active"):
    """Check if attribute value is present for given attribute.
 Args:
    element (selenium.webdriver.remote.webelement.WebElement)
    attr (basestring): attribute name e.g. "class"
    value (basestring): value in class attribute that
      indicates element is now active/opened
 Return: bool
 """
    attributes = element.get_attribute(attr)
    return value in attributes.split() if attributes != "" else False


def wait_until_alert_is_present(driver):
    """
 Wait until alert is present.
 Args: driver (base.CustomDriver)
 Return: selenium.webdriver.common.alert.Alert
 """
    return (WebDriverWait(driver, constants.ux.MAX_ALERT_WAIT).until(
        EC.alert_is_present()))


def handle_alert(driver, accept=False):
    """Wait until alert is present and make decision to accept or dismiss it."""
    try:
        wait_until_alert_is_present(driver)
        alert = driver.switch_to.alert
        if accept:
            alert.accept()
        else:
            alert.dismiss()
    except (exceptions.NoAlertPresentException, exceptions.TimeoutException):
        pass


def click_on_staleable_element(driver, el_locator):
    """Click element that can be modified between time we find it and when
 we click on it."""
    time_start = time.time()
    while time.time() - time_start < constants.ux.MAX_USER_WAIT_SECONDS:
        try:
            driver.find_element(*el_locator).click()
            break
        except exceptions.StaleElementReferenceException as err:
            LOGGER.error(err)
            time.sleep(0.1)
    else:
        raise exception.ElementNotFound(el_locator)


def scroll_into_view(driver, element):
    """Scroll page to element using JS."""
    driver.execute_script("return arguments[0].scrollIntoView(false);",
                          element)
    # compensate for the header
    driver.execute_script("window.scrollBy(0, -{});".format(
        constants.settings.SIZE_HEADER))
    return element


def wait_for_js_to_load(driver):
    """Wait until there all JS are completed."""
    return wait_until_condition(
        driver, lambda js: driver.execute_script("return jQuery.active") == 0)


def wait_for_doc_is_ready(driver):
    """Wait until current document is fully leaded.
  When 'document.readyState' has a status of "complete", it means that the
  document (example: html file) is now parsed and loaded and all known document
  subresources like CSS and images have been parsed and loaded.
  """
    return wait_until_condition(
        driver,
        lambda doc: driver.execute_script("return document.readyState") == "complete"
    )


def click_via_js(driver, element):
    """Click on element using JS."""
    driver.execute_script("arguments[0].click();", element)


def is_element_enabled(element):
    """Is this element and first parent and first level child elements is
  enabled, use when common WebDriver "isEnabled"  isn't working"""
    elements_to_check = [element, element.find_element_by_xpath("../.")]
    elements_to_check.extend(get_nested_elements(element))
    return all([
        el.is_enabled() and not is_value_in_attr(el, value="disabled")
        for el in elements_to_check
    ])


def is_element_checked(driver, element):
    """Check DOM input element checked property using JS.
  Args: driver (base.CustomDriver), locator (tuple)
  Return: True if element is checked, False if element is not checked.
  """
    return driver.execute_script("return arguments[0].checked", element)


def get_nested_elements(element, all_nested=False):
    """Get nested elements of current element by Xpath. If all_nested=True,
  return all-levels nested elements
  """
    nested_locator = './*'
    if all_nested:
        nested_locator = './/*'
    return element.find_elements_by_xpath(nested_locator)


def get_element_safe(element, locator):
    """Get element from current element by locator.
  Return "None" if element not found
  """
    return next((el for el in element.find_elements(*locator)), None)


def _send_custom_command(chromedriver, command, params):
    """Send custom command to chromedriver. For full list of commands
  take a look at Chrome Protocol doc.
  """
    # pylint: disable=protected-access
    resource = "/session/{}/chromium/send_command_and_get_result".format(
        chromedriver.session_id)
    url = chromedriver.command_executor._url + resource
    body = json.dumps({'cmd': command, 'params': params})
    response = chromedriver.command_executor._request('POST', url, body)
    return response.get('value')


def set_element_attribute(element, attr_name, attr_value):
    """Set attribute value of element's style. If attr_value is string
  it will be wrapped with double-quotes.
  """
    if isinstance(attr_value, basestring):
        attr_value = "'{0}'".format(attr_value)
    element.parent.execute_script(
        "arguments[0].setAttribute('{0}', {1})".format(attr_name,
                                                       attr_value), element)


def get_full_screenshot_as_base64(driver):
    """Get full screenshot according to size of HEADER, FOOTER and
  object area content. If InfoPanel exists, screenshot height will be increase
  according to sum of TreeView and InfoPanel size. This method manipulate with
  Viewport attribute of ChromeBrowser.
  Return: screenshot as base64.
  """

    def get_page_body_size():
        """Return dict with width and height of page size."""
        return {
            alias.HEIGHT:
            driver.execute_script(
                "return document.documentElement.scrollHeight"),
            alias.WIDTH:
            driver.execute_script(
                "return document.documentElement.scrollWidth")
        }

    def get_screenshot_by_size(width, height):
        """Change device metrics according to passed width and height, then
    do screenshot and reset device metrics.
    Return: Screenshot as base64.
    """
        _send_custom_command(driver, "Emulation.setVisibleSize", {
            alias.HEIGHT: height,
            alias.WIDTH: width
        })
        scrnshot = driver.get_screenshot_as_base64()
        _send_custom_command(driver, "Emulation.resetViewport", {})
        return scrnshot

    panel_elem = get_element_safe(driver, locators.Common.PANEL_CSS)
    panel_origin_style = None
    page_content_size = get_page_body_size()
    full_area = get_element_safe(driver, locators.Common.OBJECT_AREA_CSS)
    if panel_elem and panel_elem.size[alias.HEIGHT]:
        panel_origin_style = panel_elem.get_attribute("style")
        panel_content_size = (panel_elem.get_property(alias.SCROLL_HEIGHT) +
                              constants.settings.SIZE_PANE_HEADER)
        driver.execute_script("arguments[0].removeAttribute('style')",
                              panel_elem)
        tree_view_height = driver.find_element(
            *locators.TreeView.TREE_VIEW_CONTAINER_CSS).size[alias.HEIGHT]
        page_content_size[alias.HEIGHT] = panel_content_size + tree_view_height
    elif full_area:
        full_area_height = full_area.get_property(alias.SCROLL_HEIGHT)
        if full_area_height > page_content_size[alias.HEIGHT]:
            page_content_size[alias.HEIGHT] = full_area_height
    page_content_size[alias.HEIGHT] += (
        constants.settings.SIZE_FOOTER + constants.settings.SIZE_HEADER)
    screenshot_base64 = get_screenshot_by_size(**page_content_size)
    if panel_origin_style:
        set_element_attribute(panel_elem, "style", panel_origin_style)
    return screenshot_base64
