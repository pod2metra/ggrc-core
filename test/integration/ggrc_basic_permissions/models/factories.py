# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Factories for basic permission models"""

from ggrc_basic_permissions import models

from integration.ggrc.models.model_factory import ModelFactory


class RoleFactory(ModelFactory):
    # pylint: disable=too-few-public-methods,missing-docstring,old-style-class
    # pylint: disable=no-init

    class Meta:
        model = models.Role

    name = None
    permissions_json = None


class UserRoleFactory(ModelFactory):
    # pylint: disable=too-few-public-methods,missing-docstring,old-style-class
    # pylint: disable=no-init

    class Meta:
        model = models.UserRole


class ContextImplicationFactory(ModelFactory):
    # pylint: disable=too-few-public-methods,missing-docstring,old-style-class
    # pylint: disable=no-init

    class Meta:
        model = models.ContextImplication
