# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Functionality for work with JSON templates."""
# pylint: disable=too-few-public-methods
# pylint: disable=redefined-builtin
# pylint: disable=invalid-name

import json
import os

import inflection


class TemplateProvider(object):
    """Provider of methods for work with JSON templates."""

    @staticmethod
    def generate_template_as_dict(json_tmpl_name, **kwargs):
        """Get template as dictionary from predefined JSON file and attributes
    (items (kwargs): key=value).
    Return dictionary like as {type: {key: value, ...}}.
    """
        json_tmpl_name = inflection.underscore(json_tmpl_name)
        path = os.path.join(
            os.path.dirname(__file__),
            "template/{0}.json".format(json_tmpl_name))
        with open(path) as json_file:
            json_data = json.load(json_file)
        json_data.update({k: v for k, v in kwargs.iteritems() if v})
        return {json_tmpl_name: json_data}

    @staticmethod
    def update_template_as_dict(json_data_str, **kwargs):
        """Update JSON data string as dictionary according to
    attributes (items (kwargs): key=value).
    Return dictionary like as [{type: {key: value, ...}}].
    """
        json_data = json.loads(json_data_str)
        type = json_data.iterkeys().next()
        value = json_data.itervalues().next()
        value.update(kwargs)
        return {type: value}
