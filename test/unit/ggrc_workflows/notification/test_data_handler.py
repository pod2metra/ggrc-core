# -*- coding: utf-8 -*-

# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""A module with tests for the GGRC Workflow's data_handler module."""

import unittest
from mock import MagicMock, patch

from ggrc_workflows import models
from ggrc_workflows.notification import data_handler


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

        result = data_handler.get_cycle_task_url(task)

        expected_url = (u"http://www.foo.com/"
                        u"workflows/9#current_widget"
                        u"/cycle/77"
                        u"/cycle_task_group/6"
                        u"/cycle_task_group_object_task/15")
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

        result = data_handler.get_cycle_task_url(task, filter_exp=cycle_filter)

        expected_url = (u"http://www.foo.com/"
                        u"workflows/9?filter=id%3D77#current_widget"
                        u"/cycle/77"
                        u"/cycle_task_group/6"
                        u"/cycle_task_group_object_task/15")
        self.assertEqual(result, expected_url)


@patch(
    u"ggrc_workflows.models.cycle.get_url_root",
    return_value=u"http://www.foo.com/")
class GetCycleUrlTestCase(unittest.TestCase):
    """Tests for the get_cycle_url() function."""

    # pylint: disable=invalid-name, unused-argument

    def test_generates_correct_url_for_active_cycle(self, *mocks):
        """The method should return correct URL for active Cycles."""
        workflow = MagicMock()
        workflow.id = 111
        cycle = models.Cycle(id=22, workflow=workflow)

        # by default, a cycle is considered active
        expected_url = (u"http://www.foo.com/"
                        u"workflows/111#current_widget"
                        u"/cycle/22")
        self.assertEqual(expected_url, cycle.cycle_url)

    def test_generates_correct_url_for_inactive_cycle(self, *mocks):
        """The method should return correct URL for inactive Cycles."""
        workflow = MagicMock()
        workflow.id = 111
        cycle = models.Cycle(id=22, workflow=workflow)

        expected_url = (u"http://www.foo.com/"
                        u"workflows/111#history_widget"
                        u"/cycle/22")
        self.assertEqual(expected_url, cycle.cycle_inactive_url)
