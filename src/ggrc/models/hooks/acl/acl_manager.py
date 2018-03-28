# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Basic object_queue used by program & audit role hooks"""

from ggrc.models import all_models


class ACLManager(object):  # pylint: disable=R0903
    """Access Control List helper"""

    def __init__(self):
        self.object_queue = {}

    def get_or_create(self, obj, parent, person, role_id):
        """Add new item if it wasn't already added"""
        key = (obj.id, obj.type, person.id, role_id, parent.id)
        if key in self.object_queue:
            return self.object_queue[key]
        acl = all_models.AccessControlList(
            object_id=obj.id,
            object_type=obj.type,
            parent=parent,
            person=person,
            ac_role_id=role_id)
        self.object_queue[key] = acl
        if hasattr(obj, "access_control_list"):
            obj.access_control_list.append(acl)
        return acl
