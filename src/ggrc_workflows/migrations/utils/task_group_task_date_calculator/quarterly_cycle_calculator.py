# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Calculator for task group task start_, end_ dates in annual Workflow
"""

import datetime
from dateutil import relativedelta

from ggrc_workflows.migrations.utils.task_group_task_date_calculator import \
    cycle_calculator


class QuarterlyCycleCalculator(cycle_calculator.CycleCalculator):
    """CycleCalculator implementation for quarterly workflows.

  Quarterly workflows have a specific date domain that also requires a bit more
  math. Option 1 is for Jan/Apr/Jul/Oct, option 2 is for Feb/May/Aug/Nov and
  option 3 is for Mar/Jun/Sep/Dec. Each task can go UP TO three
  months (non-inclusive).
  """
    time_delta = relativedelta.relativedelta(months=3)

    date_domain = {
        1: {1, 4, 7, 10},  # Jan/Apr/Jul/Oct
        2: {2, 5, 8, 11},  # Feb/May/Aug/Nov
        3: {3, 6, 9, 12}  # Mar/Jun/Sep/Dec
    }

    def relative_day_to_date(self,
                             relative_day,
                             relative_month=None,
                             base_date=None):
        """Converts a quarterly representation of a day into concrete date object.

    Relative month is not the best description, but we have to standardize on
    something (better would be relative_quarter) to ensure consistent calls
    from CycleCalculator.

    First we ensure that we have both relative_day and relative_month or,
    alternatively, that relative_day carries month information as well.

    To convert from relative month and day to reified date we use a
    transformation matrix with another shifting vector to convert from modulo
    result to the correct column index (because modulo result 1 2 0 shifts to
    the right to become 0 1 2).

     index:  0  1  2 |  0  1  2 |  0  1  2 |  0  1  2
     month:  1  2  3 |  4  5  6 |  7  8  9 | 10 11 12
     x % 3:  1  2  0 |  1  2  0 |  1  2  0 |  1  2  0
     -------------------- SHIFT ---------------------
        1:   0 -1 -2 |  0 -1 -2 |  0 -1 -2 |  0 -1 -2
        2:  -2  0 -1 | -2  0 -1 | -2  0 -1 | -2  0 -1
        3:  -1 -2  0 | -1 -2  0 | -1 -2  0 | -1 -2  0

    Rows (1, 2, 3) being date domain options and values being number of months
    to shift depending on the on current date. E.g., for second date domain and
    value 2/15 on January 6th the reified value is November 15th the year
    before, that's why we have to subtract two months from today (base date).
    Because it's actually LESS than today, next cycle start date will be moved
    to February 15, but that is handled by higher-level logic.

    T = [
      [0, -1, -2],
      [-2, 0, -1],
      [-1, -2, 0]
    ]

    Afterwards we repeat the math similar to monthly cycle calculator and
    ensure that the day is not overflowing to the next month.
    """
        date_adj = False
        shift_t = [[0, -1, -2], [-2, 0, -1], [-1, -2, 0]]
        index_t = {0: 2, 2: 1, 1: 0}
        month_shift = shift_t[relative_month - 1][index_t[base_date.month % 3]]

        start_date = (datetime.date(base_date.year, base_date.month, 1) +
                      relativedelta.relativedelta(months=month_shift))
        ddate = start_date + relativedelta.relativedelta(days=relative_day - 1)

        # We want to go up to the end of the month and not over
        if ddate.month != start_date.month:
            ddate = ddate - relativedelta.relativedelta(days=ddate.day)
            date_adj = True
        return ddate, date_adj
