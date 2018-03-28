# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Cycle calculator abstract module"""

import abc

from ggrc_workflows.migrations.utils.task_group_task_date_calculator import \
    google_holidays

# pylint: disable=invalid-name


@property
def NotImplementedProperty():
    raise NotImplementedError


class CycleCalculator(object):
    """Cycle calculation for all workflow frequencies with the exception of
  one-time workflows.
  """
    __metaclass__ = abc.ABCMeta

    date_domain = NotImplementedProperty
    time_delta = NotImplementedProperty

    HOLIDAYS = google_holidays.GoogleHolidays()

    @abc.abstractmethod
    def relative_day_to_date(self,
                             relative_day,
                             relative_month=None,
                             base_date=None):
        raise NotImplementedError("Converting from relative to real date"
                                  "must be done on an instance.")

    def __init__(self, holidays=HOLIDAYS):
        """Initializes calculator based on the workflow and holidays.
    """
        self.holidays = holidays

    # pylint: disable=too-many-arguments
    def non_adjusted_task_date_range(self,
                                     relative_start_day,
                                     relative_start_month,
                                     relative_end_day,
                                     relative_end_month,
                                     base_date=None):
        """Calculates individual task's start and end date based on base_date.

    Taking base_date into account calculates individual task's start and
    end date with relative_day_to_date function provided by a specific
    implementation of a class.

    Returns start_ and end_ dates with a flag set to True is at least one of
    the dates was adjusted due to varying month days number
    """
        start_date, s_adj = self.relative_day_to_date(
            relative_start_day,
            relative_month=relative_start_month,
            base_date=base_date)

        end_date, e_adj = self.relative_day_to_date(
            relative_end_day,
            relative_month=relative_end_month,
            base_date=base_date)

        # If the end_day is before start_day, end_date is overflowing
        # to next time unit.
        if end_date < start_date:
            end_date = end_date + self.time_delta
        return start_date, end_date, s_adj or e_adj
