# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Module for date operations"""

import calendar
from datetime import datetime


def get_days_in_current_month():
    """Gets days in current month

 Return:
      int
 """
    now = datetime.now()
    _, days_in_month = calendar.monthrange(now.year, now.month)
    return days_in_month


def get_month_start(date):
    """Gets date object with date of first of month.

 Args:
      date (datetime)

 Return:
      datetime
 """
    return date.replace(day=1)


def get_month_end(date):
    """Gets month end of input date object.

 Args:
       date (datetime)

 Return:
      datetime
 """
    return date.replace(day=calendar.monthrange(date.year, date.month)[1])
