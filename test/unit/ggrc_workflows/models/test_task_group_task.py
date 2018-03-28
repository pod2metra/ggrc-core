# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Task group task unit test module."""

import unittest
import datetime

import ddt

from ggrc.models import all_models
from ggrc_workflows.models import task_group_task


@ddt.ddt
class TestTaskGroupTask(unittest.TestCase):
    """Task group task unit test class."""

    def test_validate_task_type(self):
        """Test validate start task type."""
        tgt = task_group_task.TaskGroupTask()
        self.assertRaises(ValueError, tgt.validate_task_type, "task_type",
                          "helloh")
        self.assertEqual("menu", tgt.validate_task_type("task_type", "menu"))

    def test_validate_date(self):
        """Test validate date."""
        tgt = task_group_task.TaskGroupTask()
        self.assertEqual(
            datetime.date(2002, 4, 16),
            tgt.validate_date('start_date', datetime.date(2, 4, 16)))
        self.assertEqual(
            datetime.date(2014, 7, 23),
            tgt.validate_date('start_date',
                              datetime.datetime(2014, 7, 23, 22, 5, 7)))
        self.assertEqual(
            datetime.date(2014, 7, 23),
            tgt.validate_date('start_date',
                              datetime.datetime(2014, 7, 23, 0, 0, 0)))

    def test_validate_start_date(self):
        """Test on validation start date decorator."""
        tgt = task_group_task.TaskGroupTask()
        tgt.start_date = datetime.date(16, 4, 21)
        self.assertEqual(datetime.date(2016, 4, 21), tgt.start_date)

        tgt.end_date = datetime.date(2016, 4, 21)

        tgt.start_date = datetime.date(2015, 2, 25)
        self.assertEqual(datetime.date(2015, 2, 25), tgt.start_date)

        tgt.start_date = datetime.date(2015, 6, 17)
        self.assertEqual(datetime.date(2015, 6, 17), tgt.start_date)

    DATE_COMBINATION_LIST = [
        # unit, repeat_every, repeat_multiplier, date, expected
        (
            all_models.Workflow.WEEK_UNIT,
            1,
            0,
            datetime.date(2017, 9, 15),
            datetime.date(2017, 9, 15),
        ),
        (
            all_models.Workflow.WEEK_UNIT,
            1,
            0,
            datetime.date(2017, 9, 16),
            datetime.date(2017, 9, 15),
        ),
        (
            all_models.Workflow.WEEK_UNIT,
            1,
            1,
            datetime.date(2017, 9, 15),
            datetime.date(2017, 9, 22),
        ),
        (
            all_models.Workflow.WEEK_UNIT,
            1,
            1,
            datetime.date(2017, 9, 16),
            datetime.date(2017, 9, 22),
        ),
        (
            all_models.Workflow.MONTH_UNIT,
            1,
            1,
            datetime.date(2017, 9, 16),
            datetime.date(2017, 10, 16),
        ),
        (
            all_models.Workflow.MONTH_UNIT,
            1,
            0,
            datetime.date(2017, 9, 16),
            datetime.date(2017, 9, 15),
        ),
        (
            all_models.Workflow.DAY_UNIT,
            1,
            0,
            datetime.date(2017, 9, 15),
            datetime.date(2017, 9, 15),
        ),
        (
            all_models.Workflow.DAY_UNIT,
            1,
            1,
            datetime.date(2017, 9, 15),
            datetime.date(2017, 9, 18),
        ),
        (
            None,
            None,
            0,
            datetime.date(2017, 9, 15),
            datetime.date(2017, 9, 15),
        ),
    ]

    @ddt.data(*DATE_COMBINATION_LIST)
    @ddt.unpack
    def test_show_view_start_date(  # pylint: disable=too-many-arguments
            self, unit, repeat_every, repeat_multiplier, date, expected):
        """Calculate view start date."""
        task_group = all_models.TaskGroup(workflow=all_models.Workflow())
        task_group.workflow.unit = unit
        task_group.workflow.repeat_every = repeat_every
        task_group.workflow.repeat_multiplier = repeat_multiplier
        task = task_group_task.TaskGroupTask()
        task.task_group = task_group
        task.start_date = date
        task.end_date = date + datetime.timedelta(1)
        self.assertEqual(expected, task.view_start_date)

    @ddt.data(*DATE_COMBINATION_LIST)
    @ddt.unpack
    def test_show_view_end_date(  # pylint: disable=too-many-arguments
            self, unit, repeat_every, repeat_multiplier, date, expected):
        """Calculate view end date."""
        task_group = all_models.TaskGroup(workflow=all_models.Workflow())
        task_group.workflow.unit = unit
        task_group.workflow.repeat_every = repeat_every
        task_group.workflow.repeat_multiplier = repeat_multiplier
        task = task_group_task.TaskGroupTask()
        task.task_group = task_group
        task.start_date = date - datetime.timedelta(1)
        task.end_date = date
        self.assertEqual(expected, task.view_end_date)
