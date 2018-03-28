# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Calculator for task group task start_, end_ dates in annual Workflow
"""

import datetime
from dateutil import relativedelta

from ggrc_workflows.migrations.utils.task_group_task_date_calculator import \
    cycle_calculator


class WeeklyCycleCalculator(cycle_calculator.CycleCalculator):
    """CycleCalculator implementation for weekly workflows.

  Weekly workflows have a date domain of workdays (Monday - Friday),
  calculations are based on relative_start_day and relative_end_day.
  """
    time_delta = datetime.timedelta(weeks=1)
    date_domain = {1, 2, 3, 4, 5}

    def relative_day_to_date(self,
                             relative_day,
                             relative_month=None,
                             base_date=None):
        """Converts a weekly representation of a day into concrete date object.

    Weekly relative days are represented as days in the week (1 Monday,
    5 Friday); we calculate a concrete date by adding the difference between
    target relative day and iso weekeday of the base_date.

    Example:
      If relative day is Friday (5) and base_date (cycle start date) is
      Wednesday, we don't want need to do Wednesday + 5 but Wednesday + 2 to
      get back Friday.
    """
        today = datetime.date.today()
        if relative_day not in WeeklyCycleCalculator.date_domain:
            raise ValueError(
                "Weekly recurring cycles can only have relative day in 1-5 "
                "(Monday-Friday) range")

        if not base_date:
            base_date = today

        # We want to calculate relative to Monday (1) and not relative to base_date
        # (which could be in the middle of the week)
        # We can use `weekday` method because it's 0-based method (0-6)
        base_date = base_date - relativedelta.relativedelta(
            days=base_date.weekday())

        return base_date + relativedelta.relativedelta(
            days=relative_day - 1), False  # -1 because we are counting from 1
