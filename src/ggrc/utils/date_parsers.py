# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""This module contains date parser classes"""
import re
import datetime
import calendar


class Parser(object):

    GENERAL_PATTERN = None

    @classmethod
    def is_match(cls, date):
        return re.match(cls.GENERAL_PATTERN, date)

    @staticmethod
    def parse(date):
        raise NotImplementedError()


class YearParser(Parser):
    """Class Parser year"""
    GENERAL_PATTERN = r'^\d{4}$'

    @staticmethod
    def parse(date):
        year = int(date)

        return (datetime.datetime(year, 1, 1, 0, 0, 0),
                datetime.datetime(year, 12, 31, 23, 59, 59))


class IsoMonthParser(Parser):
    """Class Parser for Iso format date time year-month"""
    GENERAL_PATTERN = r'^\d{4}-\d{1,2}$'

    @staticmethod
    def parse(date):
        year, month = [int(i) for i in re.split(r"\D", date)]

        days = calendar.monthrange(year, month)[1]
        return (datetime.datetime(year, month, 1, 0, 0, 0),
                datetime.datetime(year, month, days, 23, 59, 59))


class IsoDayParser(Parser):
    """Class Parser for Iso format date time year-month-day"""
    GENERAL_PATTERN = r'^\d{4}(-\d{1,2}){2}$'

    @staticmethod
    def parse(date):
        year, month, day = [int(i) for i in re.split(r"\D", date)]

        return (datetime.datetime(year, month, day, 0, 0, 0),
                datetime.datetime(year, month, day, 23, 59, 59))


class IsoHourParser(Parser):
    """Class Parser for Iso format date time year-month-day hour"""
    GENERAL_PATTERN = r'^\d{4}(-\d{1,2}){2} \d{1,2}$'

    @staticmethod
    def parse(date):
        year, month, day, hour = [int(i) for i in re.split(r"\D", date)]

        return (datetime.datetime(year, month, day, hour, 0, 0),
                datetime.datetime(year, month, day, hour, 59, 59))


class IsoMinuteParser(Parser):
    """Class Parser for Iso format date time year-month-day hour:minute"""
    GENERAL_PATTERN = r'^\d{4}(-\d{1,2}){2} \d{1,2}:\d{1,2}$'

    @staticmethod
    def parse(date):
        year, month, day, hour, minute = [
            int(i) for i in re.split(r"\D", date)
        ]

        return (datetime.datetime(year, month, day, hour, minute, 0),
                datetime.datetime(year, month, day, hour, minute, 59))


class IsoSecondParser(Parser):
    """Class Parser for Iso format date time year-month-day hour:minute:second"""
    GENERAL_PATTERN = r'^\d{4}(-\d{1,2}){2} \d{1,2}(:\d{1,2}){2}$'

    @staticmethod
    def parse(date):
        year, month, day, hour, minute, second = [
            int(i) for i in re.split(r"\D", date)
        ]

        return (datetime.datetime(year, month, day, hour, minute, second),
                datetime.datetime(year, month, day, hour, minute, second))


class CombineParser(Parser):

    PARSERS = []

    @classmethod
    def parse(cls, date):
        for parser in cls.PARSERS:
            if parser.is_match(date):
                return parser.parse(date)


class USSecondParser(Parser):
    """Class Parser for US format date time day/month/year hour:minute:second"""
    GENERAL_PATTERN = r'^(\d{0,2}\/){2}\d{4} \d{1,2}(:\d{1,2}){2}$'

    @staticmethod
    def parse(date):
        month, day, year, hour, minute, second = [
            int(i) for i in re.split(r"\D", date)
        ]

        return (datetime.datetime(year, month, day, hour, minute, second),
                datetime.datetime(year, month, day, hour, minute, second))


class USMinuteParser(Parser):
    """Class Parser for US format date time day/month/year hour:minute"""
    GENERAL_PATTERN = r'^(\d{0,2}\/){2}\d{4} \d{1,2}(:\d{1,2}){1}$'

    @staticmethod
    def parse(date):
        month, day, year, hour, minute = [
            int(i) for i in re.split(r"\D", date)
        ]

        return (datetime.datetime(year, month, day, hour, minute, 0),
                datetime.datetime(year, month, day, hour, minute, 59))


class USHourParser(Parser):
    """Class Parser for US format date time day/month/year hour"""
    GENERAL_PATTERN = r'^(\d{0,2}\/){2}\d{4} \d{1,2}$'

    @staticmethod
    def parse(date):
        month, day, year, hour = [int(i) for i in re.split(r"\D", date)]

        return (datetime.datetime(year, month, day, hour, 0, 0),
                datetime.datetime(year, month, day, hour, 59, 59))


class USDayParser(Parser):
    """Class Parser for US format date time day/month/year"""
    GENERAL_PATTERN = r'^(\d{0,2}\/){2}\d{4}$'

    @staticmethod
    def parse(date):
        month, day, year = [int(i) for i in re.split(r"\D", date)]

        return (datetime.datetime(year, month, day, 0, 0, 0),
                datetime.datetime(year, month, day, 23, 59, 59))


class USMonthParser(Parser):
    """Class Parser for US format date time month/year"""
    GENERAL_PATTERN = r'^(\d{0,2}\/){1}\d{4}$'

    @staticmethod
    def parse(date):
        month, year = [int(i) for i in re.split(r"\D", date)]

        days = calendar.monthrange(year, month)[1]
        return (datetime.datetime(year, month, 1, 0, 0, 0),
                datetime.datetime(year, month, days, 23, 59, 59))


def combiner_factory(name, pattern, parsers):
    return type(name, (CombineParser, ), {
        "GENERAL_PATTERN": pattern,
        "PARSERS": parsers
    })


USCombiner = combiner_factory(  # pylint: disable=invalid-name
    "USCombiner", r'^(\d{0,2}\/){0,2}(\d{4})(( \d{1,2}(:\d{1,2}){0,2})?)$', [
        USSecondParser, USMinuteParser, USHourParser, USDayParser,
        USMonthParser, YearParser
    ])

IsoCombiner = combiner_factory(  # pylint: disable=invalid-name
    "IsoCombiner", r'^\d{4}(-\d{1,2}){0,2}(( \d{1,2})(:\d{1,2}){0,2})?$', [
        IsoSecondParser, IsoMinuteParser, IsoHourParser, IsoDayParser,
        IsoMonthParser, YearParser
    ])

DEFAULT_PARSERS = [IsoCombiner, USCombiner]


def parse_date(date, parsers=None):
    """Try to parse sended date string"""
    parsers = parsers or DEFAULT_PARSERS
    for parser in parsers:
        if parser.is_match(date):
            return parser.parse(date)
