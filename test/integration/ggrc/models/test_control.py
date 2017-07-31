# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Tests for control model."""

from ggrc import db
from ggrc.models import Control
from integration.ggrc import TestCase
from integration.ggrc.models import factories
from integration.ggrc import api_helper


class TestControl(TestCase):
  """Tests for control model."""

  def setUp(self):
    """setUp, nothing else to add."""
    super(TestControl, self).setUp()
    self.api = api_helper.Api()

  def test_simple_categorization(self):
    """Check append category append to control."""
    category = factories.ControlCategoryFactory(scope_id=100)
    control = factories.ControlFactory()
    control.categories.append(category)
    db.session.commit()
    self.assertIn(category, control.categories)
    # be really really sure
    control = db.session.query(Control).get(control.id)
    self.assertIn(category, control.categories)

  def test_has_test_plan(self):
    """Check test plan setup to control."""
    control = factories.ControlFactory(test_plan="This is a test text")
    control = db.session.query(Control).get(control.id)
    self.assertEqual(control.test_plan, "This is a test text")

  def test_set_end_date(self):
    """End_date can't to be updated."""
    control = factories.ControlFactory()
    self.api.put(control, {"end_date": "2015-10-10"})
    control = db.session.query(Control).get(control.id)
    self.assertIsNone(control.end_date)

  def test_set_deprecated_status(self):
    """Deprecated status setup end_date."""
    control = factories.ControlFactory()
    self.assertIsNone(control.end_date)
    self.api.put(control, {"status": Control.DEPRECATED})
    control = db.session.query(Control).get(control.id)
    self.assertIsNotNone(control.end_date)
