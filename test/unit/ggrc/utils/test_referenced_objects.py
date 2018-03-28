# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Unit tests for checking referened_objects methods."""

import collections
import unittest

from mock import patch


class TestReferencedObjects(unittest.TestCase):
    """Test case for referenced objects"""

    def setUp(self):
        """Set up for test cases."""
        super(TestReferencedObjects, self).setUp()
        self.type_ = 'SomeModel'  # Model has been deleted
        self.id_ = 1  # id of the object in the db

    @patch('ggrc.models.inflector.get_model')
    def test_get_table_not_exists(self, get_model):
        """Tests getting object for deleted table."""
        from ggrc.utils.referenced_objects import get
        get_model.return_value = None
        with patch('flask.g', {}):
            result = get(self.type_, self.id_)
        self.assertIsNone(result)

    @patch('flask.g')
    @patch('ggrc.models.inflector.get_model')
    def test_mark_to_cache(self, get_model, flask_g):
        """Test for adding objects to cache for deleted table."""
        from ggrc.utils.referenced_objects import mark_to_cache
        get_model.return_value = None
        with patch.object(flask_g, 'referenced_objects_markers',
                          collections.defaultdict(set)) as cache_dict:
            mark_to_cache(self.type_, self.id_)
            self.assertFalse(None in cache_dict.keys())
