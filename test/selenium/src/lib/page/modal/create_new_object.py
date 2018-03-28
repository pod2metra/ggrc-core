# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Modals for create objects."""

from lib import base, decorator
from lib.constants import locator
from lib.page.modal import base as modal_base
from lib.utils import selenium_utils


class CreateNewObjectModal(modal_base.BaseModal):
    """Modal for create objects."""
    _locators = locator.ModalCreateNewObject

    def __init__(self, driver):
        super(CreateNewObjectModal, self).__init__(driver)

    def save_and_add_other(self):
        """Create object and open new Create modal."""
        base.Button(self._driver,
                    self._locators.BUTTON_SAVE_AND_ADD_ANOTHER).click()
        selenium_utils.get_when_invisible(
            self._driver, self._locators.BUTTON_SAVE_AND_ADD_ANOTHER)
        return self.__class__(self._driver)

    @decorator.wait_for_redirect
    @decorator.handle_alert
    def save_and_close(self):
        """Create object and close Creation modal."""
        self.button_save_and_close.click()
        selenium_utils.wait_until_not_present(self._driver,
                                              self._locator_button_save)


class ProgramsCreate(modal_base.ProgramsModal, CreateNewObjectModal):
    # pylint: disable=abstract-method
    """Programs create modal."""


class ControlsCreate(modal_base.ControlsModal, CreateNewObjectModal):
    """Controls create modal."""


class ObjectivesCreate(modal_base.ObjectivesModal, CreateNewObjectModal):
    """Objectives create modal."""


class OrgGroupsCreate(modal_base.OrgGroupsModal, CreateNewObjectModal):
    """Org Groups create modal."""


class RisksCreate(modal_base.RisksModal, CreateNewObjectModal):
    """Risks create modal."""


class IssuesCreate(modal_base.IssuesModal, CreateNewObjectModal):
    """Issues create modal."""


class ProcessesCreate(modal_base.ProcessesModal, CreateNewObjectModal):
    """Processes create modal."""


class DataAssetsCreate(modal_base.DataAssetsModal, CreateNewObjectModal):
    """Data Assets create modal."""


class SystemsCreate(modal_base.SystemsModal, CreateNewObjectModal):
    """Systems create modal."""


class ProductsCreate(modal_base.ProductsModal, CreateNewObjectModal):
    """Products create modal."""


class ProjectsCreate(modal_base.ProjectsModal, CreateNewObjectModal):
    """Projects create modal."""


class AssessmentTemplatesCreate(modal_base.AsmtTmplModal,
                                CreateNewObjectModal):
    """Assessment Templates create modal."""


class AssessmentsCreate(modal_base.AsmtsModal, CreateNewObjectModal):
    """Assessments create modal."""
