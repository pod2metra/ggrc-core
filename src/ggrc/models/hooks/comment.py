# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""A module with Comment object creation hooks"""
from sqlalchemy import event

from ggrc.access_control import role
from ggrc.login import get_current_user
from ggrc.models.all_models import Comment, AccessControlList
from ggrc.models import comment
from ggrc.models import all_models
from ggrc.access_control import roleable
from ggrc.access_control import list as ACL


def propagate_acl(instance, comments=None):
  """Propagate instance ACL to comments."""
  if not isinstance(instance, comment.Commentable):
    return
  if not isinstance(instance, roleable.Roleable):
    return
  append_roles = []
  roles = {r.name: r for r in
           role.AccessControlRole.query.filter(
               role.AccessControlRole.object_type == "Comment"
           )}
  for acl in instance.access_control_list:
    if acl.ac_role is None:
      # FIXME: this can happend only on propagation now
      # should be fixed on ACL manager
      acl.ac_role = all_models.AccessControlRole.query.get(acl.ac_role_id)
    if acl.ac_role.read:
      append_roles.append((acl, roles["CommentReader"]))
  if comments is None:
    comments = instance.comments
  for comment_instance in comments:
    parents = {i.parent_id for i in comment_instance.access_control_list}
    for acl, ac_role in append_roles:
      if acl.id in parents:
        continue
      ACL.AccessControlList(
          person=acl.person,
          object=comment_instance,
          ac_role=ac_role,
          parent=acl)


def propagate_acl_over_relationship(relationship):
  """Propagate instance ACL to comments over relationship."""
  if not isinstance(relationship, all_models.Relationship):
    return
  if relationship.source_type == "Comment":
    instance = relationship.destination
    instance_comment = relationship.source
  elif relationship.destination_type == "Comment":
    instance = relationship.source
    instance_comment = relationship.destination
  else:
    return
  propagate_acl(instance, comments=[instance_comment])


def init_hook():
  """Initialize all hooks"""
  # pylint: disable=unused-variable
  # pylint: disable=unused-argument
  @event.listens_for(Comment, "after_insert")
  def handle_comment_post(mapper, connection, target):
    """Save information on which user created the Comment object."""
    # pylint: disable=unused-argument
    for role_id, role_name in role.get_custom_roles_for(target.type).items():
      user = get_current_user()
      if role_name == "Admin" and not user.is_anonymous():
        AccessControlList(
            ac_role_id=role_id,
            person=user,
            object=target,
        )
        return

  for model in all_models.all_models:
    @event.listens_for(model, "after_insert")
    def handle_instance_post(mapper, connection, target):
      """Propagate permissions to comment."""
      propagate_acl_over_relationship(target)
      propagate_acl(target)
