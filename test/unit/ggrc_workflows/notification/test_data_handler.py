# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""A module with tests for the GGRC Workflow's data_handler module."""

import unittest

from mock import MagicMock, patch

from ggrc import extensions
from ggrc_workflows.notification.data_handler import get_cycle_task_url
from ggrc_workflows import notification


class GetCycleTaskUrlTestCase(unittest.TestCase):
  """Tests for the get_cycle_task_url() function."""

  # pylint: disable=invalid-name, unused-argument
  @patch(
      u"ggrc_workflows.notification.data_handler.get_url_root",
      return_value=u"http://www.foo.com/")
  def test_generates_correct_url_for_task(self, *mocks):
    """The method should return a correct URL for the given Task."""
    task = MagicMock()
    task.id = 15
    task.cycle_task_group.id = 6
    task.cycle_task_group.cycle.id = 77
    task.cycle_task_group.cycle.workflow.id = 9

    result = get_cycle_task_url(task)

    expected_url = (
        u"http://www.foo.com/"
        u"workflows/9#current_widget"
        u"/cycle/77"
        u"/cycle_task_group/6"
        u"/cycle_task_group_object_task/15"
    )
    self.assertEqual(result, expected_url)

  # pylint: disable=invalid-name, unused-argument
  @patch(
      u"ggrc_workflows.notification.data_handler.get_url_root",
      return_value=u"http://www.foo.com/")
  def test_generates_correct_url_with_filter_if_given(self, *mocks):
    """The method should return a correct URL for the given Task."""
    task = MagicMock()
    task.id = 15
    task.cycle_task_group.id = 6
    task.cycle_task_group.cycle.id = 77
    task.cycle_task_group.cycle.workflow.id = 9

    cycle_filter = u"id=77"

    result = get_cycle_task_url(task, filter_exp=cycle_filter)

    expected_url = (
        u"http://www.foo.com/"
        u"workflows/9?filter=id%3D77#current_widget"
        u"/cycle/77"
        u"/cycle_task_group/6"
        u"/cycle_task_group_object_task/15"
    )
    self.assertEqual(result, expected_url)


class TestHandlers(unittest.TestCase):
  """Test if handlers setup for ggrc_workflows app """

  def test_if_handler_exists(self):
    self.assertIn(
        notification.register_listeners,
        extensions.get_module_contributions("NOTIFICATION_LISTENERS")
    )
