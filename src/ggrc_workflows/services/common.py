# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

import collections

from blinker import Namespace


class Signals():
  signals = Namespace()
  StatusChangeSignalObjectContext = collections.namedtuple(
      "StatusChangeSignalObjectContext",
      ["instance", "old_status", "new_status"])
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
