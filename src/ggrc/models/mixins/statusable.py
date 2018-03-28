# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""A mixin for objects with statuses"""

from sqlalchemy.ext.declarative import declared_attr

from ggrc import db
from ggrc.models.deferred import deferred


class Statusable(object):
    """Mixin with default labels for status field"""

    # pylint: disable=too-few-public-methods

    START_STATE = u"Not Started"
    PROGRESS_STATE = u"In Progress"
    DONE_STATE = u"In Review"
    VERIFIED_STATE = u"Verified"
    FINAL_STATE = u"Completed"
    DEPRECATED = u"Deprecated"
    END_STATES = {VERIFIED_STATE, FINAL_STATE}
    INACTIVE_STATES = {
        DEPRECATED,
    }

    NOT_DONE_STATES = {START_STATE, PROGRESS_STATE}
    DONE_STATES = {DONE_STATE} | END_STATES
    VALID_STATES = tuple(NOT_DONE_STATES | DONE_STATES | INACTIVE_STATES)

    @declared_attr
    def status(cls):  # pylint: disable=no-self-argument
        return deferred(
            db.Column(
                db.Enum(*cls.VALID_STATES),
                nullable=False,
                default=cls.default_status()), cls.__name__)

    _aliases = {
        "status": {
            "display_name": "State",
            "mandatory": False,
            "description": "Options are:\n{}".format('\n'.join(VALID_STATES))
        }
    }

    @classmethod
    def default_status(cls):
        return cls.START_STATE
