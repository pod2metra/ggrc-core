# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Tests for an object states."""

import unittest

from ggrc.models import all_models


class TestStates(unittest.TestCase):
    """Tests for an object states."""

    def test_task_states(self):
        """Test task states"""
        self.assertEqual(
            all_models.CycleTaskGroupObjectTask.NO_VALIDATION_STATES,
            ["Assigned", "In Progress", "Finished", "Deprecated"])

        self.assertEqual(all_models.CycleTaskGroupObjectTask.VALID_STATES, [
            "Assigned", "In Progress", "Finished", "Deprecated", "Verified",
            "Declined"
        ])
