# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Contains the Assignable mixin.

This allows adding various assignee types to the object, like Verifiers,
Creators, etc.
"""

from collections import defaultdict

from ggrc.access_control.roleable import Roleable


class Assignable(Roleable):
    """Mixin for models with assignees"""

    ASSIGNEE_TYPES = {"Creators", "Assignees", "Verifiers"}

    @property
    def assignees(self):
        """Returns assignees.

    Returns:
        A set of assignees.
    """
        assignees = defaultdict(list)
        for acl in self.access_control_list:
            if acl.ac_role.name in self.ASSIGNEE_TYPES:
                assignees[acl.person].append(acl.ac_role.name)

        return assignees
