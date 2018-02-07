# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Test for comment permissions."""

import json

import ddt

from ggrc.models import all_models
from ggrc.models.hooks import comment as comment_hooks

from integration.ggrc import TestCase
from integration.ggrc.api_helper import Api
from integration.ggrc.models import factories
from integration.ggrc_basic_permissions.models \
    import factories as rbac_factories


@ddt.ddt
class TestPermissions(TestCase):
  """Test checks permissions for comments."""

  def setUp(self):
    super(TestPermissions, self).setUp()
    self.api = Api()
    roles = {r.name: r for r in all_models.Role.query.all()}
    with factories.single_commit():
      self.control = factories.ControlFactory()
      acrs = {
          "ACL_Reader": factories.AccessControlRoleFactory(
              name="ACL_Reader",
              object_type="Control",
              update=0),
          "ACL_Editor": factories.AccessControlRoleFactory(
              name="ACL_Editor",
              object_type="Control"),
      }
      self.comment = factories.CommentFactory()
      factories.RelationshipFactory(source=self.comment,
                                    destination=self.control)
      self.people = {
          "Creator": factories.PersonFactory(),
          "Reader": factories.PersonFactory(),
          "Editor": factories.PersonFactory(),
          "Administrator": factories.PersonFactory(),
          "ACL_Reader": factories.PersonFactory(),
          "ACL_Editor": factories.PersonFactory(),
      }
      for role_name in ["Creator", "Reader", "Editor", "Administrator"]:
        rbac_factories.UserRoleFactory(role=roles[role_name],
                                       person=self.people[role_name])
      for role_name in ["ACL_Reader", "ACL_Editor"]:
        rbac_factories.UserRoleFactory(role=roles["Creator"],
                                       person=self.people[role_name])
        factories.AccessControlListFactory(
            ac_role=acrs[role_name],
            object=self.control,
            person=self.people[role_name])
    with factories.single_commit():
      comment_hooks.propagate_acl(self.control)

  @ddt.data(
      ("Creator", 403),
      ("Reader", 200),
      ("Editor", 200),
      ("Administrator", 200),
      ("ACL_Reader", 200),
      ("ACL_Editor", 200),
  )
  @ddt.unpack
  def test_permissions_on_get(self, role_name, status):
    """Test get comments for {0}."""
    comment_id = self.comment.id
    self.api.set_user(self.people[role_name])
    self.client.get("/login")
    resp = self.api.get(all_models.Comment, comment_id)
    self.assertEqual(status, resp.status_code)

  @ddt.data(
      ("Creator", 403),
      ("Reader", 201),
      ("Editor", 201),
      ("Administrator", 201),
      ("ACL_Reader", 201),
      ("ACL_Editor", 201),
  )
  @ddt.unpack
  def test_permissions_on_create(self, role_name, status):
    """Test create comments for {0}."""
    control_id = self.control.id
    self.api.set_user(self.people[role_name])
    resp = self.api.post(
        all_models.Comment,
        {
            "comment": {
                "description": "<p>tmp_desc</p>",
                "assignee_type": "Admin",
                "send_notification": True,
                "comment": None,
                "context": None,
                "created_at": "2018-02-07T11:17:06.469Z",
            },
        },
    )
    self.client.get("/login")
    # Everyone can create the comments
    self.assertEqual(201, resp.status_code)
    new_comment_id = resp.json["comment"]["id"]
    new_comment = all_models.Comment.query.get(new_comment_id)
    parent_roles = [l.parent.ac_role.name
                    for l in new_comment.access_control_list
                    if l.parent]
    self.assertEqual(0, len(parent_roles))
    resp = self.api.post(
        all_models.Relationship,
        {
            "relationship": {
                "context": None,
                "destination": {
                    "type": "Comment",
                    "id": new_comment_id,
                },
                "source": {
                    "type": "Control",
                    "id": control_id,
                },
            },
        },
    )
    self.assertEqual(status, resp.status_code)
    new_comment = all_models.Comment.query.get(new_comment_id)
    parent_roles = [l.parent.ac_role.name
                    for l in new_comment.access_control_list
                    if l.parent]
    if status == 201:
      self.assertIn("ACL_Reader", parent_roles)
      self.assertIn("ACL_Editor", parent_roles)
    else:
      self.assertEqual(0, len(parent_roles))

  @ddt.data(
      ("Creator", 0),
      ("Reader", 1),
      ("Editor", 1),
      ("Administrator", 1),
      ("ACL_Reader", 1),
      ("ACL_Editor", 1),
  )
  @ddt.unpack
  def test_query_filter(self, role_name, not_empty):
    """Test query comments for {0}."""
    control_id = self.control.id
    data = [{
        "limit": [0, 5],
        "object_name": "Comment",
        "order_by": [{"name": "created_at", "desc": True}],
        "filters": {
            "expression": {
                "object_name": "Control",
                "op": {"name": "relevant"},
                "ids": [control_id],
            },
        },
    }]
    self.api.set_user(self.people[role_name])
    self.client.get("/login")
    headers = {"Content-Type": "application/json", }
    resp = self.api.client.post("/query",
                                data=json.dumps(data),
                                headers=headers).json
    self.assertEqual(1, len(resp))
    self.assertEqual(not_empty, resp[0]["Comment"]["count"])
