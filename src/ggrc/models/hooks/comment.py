# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""A module with Comment object creation hooks"""

from ggrc import login
from ggrc.models import all_models
from ggrc.access_control import role
from ggrc.services import signals


def init_hook():
    """Initialize all hooks"""
    # pylint: disable=unused-variable
    @signals.Restful.collection_posted.connect_via(all_models.Comment)
    def handle_comment_post(mapper, objects, **kwargs):
        """Save information on which user created the Comment object.

    Comments have their users set in a hook, because we must ensure that it is
    always set to the current user, and that is why the info is not sent from
    the front-end through access_control_list property.
    """
        # pylint: disable=unused-argument
        comment_roles = role.get_ac_roles_for(all_models.Comment.__name__)
        comment_admin = comment_roles["Admin"]
        user = login.get_current_user()
        for comment in objects:
            all_models.AccessControlList(
                ac_role=comment_admin,
                person=user,
                object=comment,
            )
