# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

import sys
from ggrc import settings
import ggrc


def get_extension_name(extension_setting, default):
    extension_name = getattr(settings, extension_setting, default)
    if extension_name is not None:
        extension_name = extension_name if not callable(extension_name) else \
            extension_name()
    else:
        extension_name = default
    return extension_name


def get_extension_modules(modules=[]):
    if len(modules) == 0:
        extension_names = getattr(settings, 'EXTENSIONS')
        if extension_names is None:
            modules.append(None)
        else:
            for m in settings.EXTENSIONS:
                modules.append(get_extension_module(m))
    if len(modules) == 0 or modules[0] is None:
        return []
    else:
        return modules


def get_extension_module(module_name):
    __import__(module_name)
    return sys.modules[module_name]


def get_extension_module_for(extension_setting, default, extension_modules={}):
    if extension_setting not in extension_modules:
        extension_name = get_extension_name(extension_setting, default)
        if not extension_name:
            extension_modules[extension_setting] = extension_name
        else:
            __import__(extension_name)
            extension_modules[extension_setting] = sys.modules[extension_name]
    return extension_modules[extension_setting]


def get_extension_instance(extension_setting, default, extensions={}):
    if extension_setting not in extensions:
        extension_name = get_extension_name(extension_setting, default)
        idx = extension_name.rfind('.')
        module_name = extension_name[0:idx]
        class_name = extension_name[idx + 1:]
        __import__(module_name)
        module = sys.modules[module_name]
        extensions[extension_setting] = getattr(module, class_name)(settings)
    return extensions[extension_setting]


def _get_contributions(module, name):
    """Fetch contributions from a single module.

  Args:
    module: Python module that will be checked for a given attribute.
    name: Name of the attribute that we want to collect from a module. The
      attribute must be a list or a callable that returns a list.

  Returns:
    List of contributions found

  Raises:
    TypeError: If the attribute is not a list or a callable that returns a
      list.
  """
    contributions = getattr(module, name, [])
    if callable(contributions):
        contributions = contributions()

    if isinstance(contributions, dict):
        contributions = contributions.items()
    if not isinstance(contributions, list):
        raise TypeError("Contributed item must be a list or a callable that "
                        "returns a list")
    return contributions


def get_module_contributions(name):
    """Fetch contributions from all modules if they exist.

  This function loops through all modules and checks if the main module package
  contains attribute with a given name or if it cotnains contributions which
  have an attribute with the said name. It gathers all such attributes in a
  list and returns it.

  Args:
    name (string): name of the contributed attribute that will be collected.

  Returns:
    A list of all collected attributes.

  """
    all_contributions = []
    all_modules = [ggrc] + get_extension_modules()
    for module in all_modules:
        all_contributions.extend(_get_contributions(module, name))
        contributions_module = getattr(module, "contributions", None)
        if contributions_module:
            all_contributions.extend(
                _get_contributions(contributions_module, name))
    if all(isinstance(val, tuple) for val in all_contributions):
        all_contributions = dict(all_contributions)
    return all_contributions
