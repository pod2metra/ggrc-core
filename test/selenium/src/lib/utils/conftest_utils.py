# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""PyTest fixture utils."""

from lib import cache, constants, factory
from lib.page import dashboard
from lib.utils import selenium_utils


def get_lhn_accordion(driver, object_name):
    """Select relevant section in LHN and return relevant section accordion."""
    selenium_utils.open_url(driver, dashboard.Dashboard.URL)
    lhn_menu = dashboard.Header(driver).open_lhn_menu()
    # if object button not visible, open this section first
    if object_name in cache.LHN_SECTION_MEMBERS:
        method_name = factory.get_method_lhn_select(object_name)
        lhn_menu = getattr(lhn_menu, method_name)()
    return getattr(lhn_menu, constants.method.SELECT_PREFIX + object_name)()


def create_obj_via_lhn(driver, object_name):
    """Create object via LHN."""
    modal = get_lhn_accordion(driver, object_name).create_new()
    factory.get_cls_test_utils(object_name).enter_test_data(modal)
    modal.save_and_close()
    return factory.get_cls_widget(object_name, is_info=True)(driver)


def delete_obj_via_info_widget(driver, object_name):
    """Delete object via Info Widget."""
    (factory.get_cls_widget(object_name, is_info=True)(driver)
     .open_3bbs().select_delete().confirm_delete())
