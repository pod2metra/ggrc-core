# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Google internal holidays list
"""
from datetime import date

import holidays


class GoogleHolidays(holidays.UnitedStates):
    def _populate(self, year):
        super(GoogleHolidays, self)._populate(year)

        if year < 2017:
            self[date(year, 11, 27)] = "Thanksgiving Day 2"
            self[date(year, 12, 23)] = "Christmas Holiday"
            self[date(year, 12, 24)] = "Christmas Eve"
            self[date(year, 12, 31)] = "New Year's Eve"
        elif year == 2017:
            self[date(year, 1, 2)] = "New Year's Day"
            self[date(year, 1, 16)] = "Martin Luther King Day"
            self[date(year, 2, 20)] = "Presidents' Day"
            self[date(year, 5, 29)] = "Memorial Day"
            self[date(year, 7, 3)] = "Independence Day Holiday"
            self[date(year, 7, 4)] = "Independence Day"
            self[date(year, 9, 4)] = "Labor Day"
            self[date(year, 11, 23)] = "Thanksgiving Day"
            self[date(year, 11, 24)] = "Thanksgiving Holiday"
            self[date(year, 12, 25)] = "Christmas Day"
            self[date(year, 12, 26)] = "Christmas Holiday"
            self[date(year, 12, 29)] = "New Year's Holiday"
