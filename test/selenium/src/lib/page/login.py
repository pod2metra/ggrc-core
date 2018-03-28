# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Login page."""

from lib import environment, base
from lib.constants import locator
from lib.page import dashboard


class LoginPage(base.Page):
    """Login page model."""

    URL = environment.APP_URL

    def __init__(self, driver):
        super(LoginPage, self).__init__(driver)
        self.button_login = base.Button(driver, locator.Login.BUTTON_LOGIN)

    def login(self):
        """Click on login button on Login page
    Return: dashboard.Dashboard
    """
        self.button_login.click()
        return dashboard.Dashboard(self._driver)

    def login_as(self, user_name, user_email):
        """Click on login button on Login page and logs in as certain user.
    """
        raise NotImplementedError
