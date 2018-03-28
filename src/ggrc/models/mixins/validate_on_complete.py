# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Contains ValidateOnComplete mixin.

This defines a procedure of an object's validation when its status moves from
one of NOT_DONE_STATES to DONE_STATES.
"""

from sqlalchemy.orm import validates

from ggrc.models.exceptions import ValidationError


class ValidateOnComplete(object):
    """Defines the validation routine before marking an object as complete.

  Requires Stateful and Statusable to be mixed in as well."""

    skip_validation = False

    # pylint: disable=too-few-public-methods
    @validates("status")
    def validate_status(self, key, value):
        """Check that no CA-introduced completion preconditions are missing."""
        # support for multiple validators for status
        if hasattr(super(ValidateOnComplete, self), "validate_status"):
            value = super(ValidateOnComplete, self).validate_status(key, value)
        self.validate_done_state(self.status, value)
        return value

    def validate_done_state(self, old_value, new_value):
        """Check if it's allowed to set done state from not done.

    Args:
        old_value: Old state (Assessment.VALID_STATES).
        new_value: New state (Assessment.VALID_STATES).

    Raise:
        ValidationError if state can't be changed.
    """
        if not self.skip_validation and \
           old_value in self.NOT_DONE_STATES and \
           new_value in self.DONE_STATES:
            if hasattr(self,
                       "preconditions_failed") and self.preconditions_failed:
                raise ValidationError(
                    "CA-introduced completion preconditions "
                    "are not satisfied. Check preconditions_failed "
                    "of items of self.custom_attribute_values")
