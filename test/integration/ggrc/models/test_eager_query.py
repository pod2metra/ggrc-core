# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Tests for making sure eager queries are working on all mixins."""

from ggrc.models import all_models
from ggrc.models import mixins
from integration.ggrc import TestCase


class TestAllModels(TestCase):
    """Test basic model structure for all models"""

    def test_all_model_mro(self):
        """Test the correct mixin order for eager queries.

    This test checks that all models that have an eager query, have the last
    mixin in the mro Identifiable. If there are any other mixins with eager
    query after it, the eager query on those is ignored and that is an error.
    """
        errors = set()
        for model in all_models.all_models:
            eager = [
                mixin for mixin in model.mro()
                if hasattr(mixin, "eager_query")
            ]
            if eager:
                try:
                    self.assertEqual(
                        eager[-1],
                        mixins.base.Identifiable,
                        "Model {}, has wrong mixin order. The last mixin with "
                        "eager_query is '{}' instead of 'Identifiable'.".
                        format(model.__name__, eager[-1].__name__),
                    )
                except AssertionError as error:
                    errors.add(error)
        self.assertEqual(set(), errors)
