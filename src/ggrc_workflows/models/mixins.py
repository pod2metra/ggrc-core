# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Mixins for ggrc_workflow app."""

from datetime import date

from sqlalchemy.ext import declarative

from ggrc import builder
from ggrc import db
from ggrc.models import deferred
from ggrc.models import mixins
from ggrc.models import reflection


class RelativeTimeboxed(mixins.Timeboxed):
  # Frequencies and offset:
  #   annual:
  #     month is the 0-indexed month (0 is January)
  #     day is the 0-indexed offset day
  #   quarterly:
  #     month is in [0,1,2], as the offset within the quarter
  #     day is same as annual
  #   weekly:
  #     month is ignored
  #     day is in [1,2,3,4,5] where 0 is Monday

  relative_start_month = db.Column(db.Integer, nullable=True)
  relative_start_day = db.Column(db.Integer, nullable=True)
  relative_end_month = db.Column(db.Integer, nullable=True)
  relative_end_day = db.Column(db.Integer, nullable=True)


class StatusValidatedMixin(mixins.Stateful):
  """Mixin setup statuses for Cycle and CycleTaskGroup."""

  ASSIGNED = u"Assigned"
  IN_PROGRESS = u"InProgress"
  FINISHED = u"Finished"
  VERIFIED = u"Verified"

  NO_VALIDATION_STATES = [ASSIGNED, IN_PROGRESS, FINISHED]
  VALID_STATES = NO_VALIDATION_STATES + [VERIFIED]

  _api_attrs = reflection.ApiAttributes(
      reflection.Attribute("is_verification_needed",
                           create=False,
                           update=False),
  )

  def is_verification_needed(self):
    raise NotImplementedError()

  @classmethod
  def default_status(cls):
    return cls.ASSIGNED

  def valid_statuses(self):
    """Return valid status for self instance."""
    if self.is_verification_needed:
      return self.VALID_STATES
    return self.NO_VALIDATION_STATES

  @property
  def active_states(self):
    return [i for i in self.valid_statuses() if i != self.done_status]

  @property
  def done_status(self):
    return self.VERIFIED if self.is_verification_needed else self.FINISHED

  @property
  def is_done(self):
    return self.done_status == self.status


class CycleStatusValidatedMixin(StatusValidatedMixin):
  """Mixin setup is_verification needed field for Cycle."""

  _aliases = {
      "status": {
          "display_name": "State",
          "mandatory": False,
          "description": "Options are: \n{} ".format(
              '\n'.join(StatusValidatedMixin.VALID_STATES)
          ),
      },
  }

  @declarative.declared_attr
  def is_verification_needed(cls):  # pylint: disable=no-self-argument
    return deferred.deferred(
        db.Column(db.Boolean, default=True, nullable=False),
        cls.__name__,
    )


class CycleTaskGroupRelatedStatusValidatedMixin(StatusValidatedMixin):
  """Mixin setup is_verification needed property."""

  @builder.simple_property
  def is_verification_needed(self):
    return self.cycle is None or self.cycle.is_verification_needed


class CycleTaskStatusValidatedMixin(CycleTaskGroupRelatedStatusValidatedMixin):
  """Mixin setup state for CycleTaskGroupObjectTask."""

  DECLINED = u"Declined"

  VALID_STATES = CycleTaskGroupRelatedStatusValidatedMixin.VALID_STATES + [
      DECLINED,
  ]

  @property
  def is_overdue(self):
    """Return True if task is overdue."""
    today = date.today()
    task_end_date = self.end_date or today
    return not self.is_done and task_end_date < today

  _aliases = {
      "status": {
          "display_name": "State",
          "mandatory": False,
          "description": "Options are: \n{} ".format('\n'.join(VALID_STATES)),
      },
  }
