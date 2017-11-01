# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

import collections

from blinker import Namespace


class Signals():
  signals = Namespace()

  # Special instance to collect context for each instance,
  # required for status_change signal handling
  StatusChangeSignalObjectContext = collections.namedtuple(
      "StatusChangeSignalObjectContext",
      [
          "instance",  # instance, with modified status
          "old_status",  # old status value
          "new_status",  # new status value
      ],
  )

  status_change = signals.signal(
      'Status Changed',
      """
    This is used to signal any listeners of any changes in model object status
    attribute
    """)

  workflow_cycle_start = signals.signal(
      'Workflow Cycle Started ',
      """
    This is used to signal any listeners of any workflow cycle start
    attribute
    """)
