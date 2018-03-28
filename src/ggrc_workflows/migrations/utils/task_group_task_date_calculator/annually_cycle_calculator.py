# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Calculator for task group task start_, end_ dates in annual Workflow
"""

import datetime
from dateutil import relativedelta

from ggrc_workflows.migrations.utils.task_group_task_date_calculator import \
    cycle_calculator


class AnnuallyCycleCalculator(cycle_calculator.CycleCalculator):
    """CycleCalculator implementation for annual workflows.

  Month domain is 1-12, date domain is 1-31.
  """

    time_delta = relativedelta.relativedelta(years=1)
    date_domain = {
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
        21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31
    }
    month_domain = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12}

    def relative_day_to_date(self,
                             relative_day,
                             relative_month=None,
                             base_date=None):
        """Converts an annual relative day representation to concrete date object

    First we ensure that we have both relative_day and relative_month or,
    alternatively, that relative_day carries month information as well.

    While task_date_range calls with explicit relative_month, reified_tasks
    stores relative days as MM/DD and we must first convert these values so
    that it can sort and get min and max values for tasks.

    Afterwards we repeat the math similar to monthly cycle calculator and
    ensure that the day is not overflowing to the next month.
    """
        date_adj = False
        if relative_day not in AnnuallyCycleCalculator.date_domain:
            raise ValueError("Annually recurring cycles can only "
                             "have relative day in 1-31 range.")

        if relative_month not in AnnuallyCycleCalculator.month_domain:
            raise ValueError("Annually recurring cycles can only "
                             "have relative month in 1-12 range.")

        start_month = datetime.date(base_date.year, relative_month, 1)
        ddate = start_month + relativedelta.relativedelta(
            days=relative_day - 1)

        # We want to go up to the end of the month and not over
        if ddate.month != start_month.month:
            ddate = ddate - relativedelta.relativedelta(days=ddate.day)
            date_adj = True
        return ddate, date_adj
