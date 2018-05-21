# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Tests for /api/comments endpoints."""

import ddt

from ggrc.models import all_models

from integration.ggrc import services
from integration.ggrc.api_helper import Api
from integration.ggrc.models import factories
from integration.ggrc_basic_permissions.models import factories \
    as rbac_factories


@ddt.ddt
class TestCommentResource(services.TestCase):
  """Tests for special comment api endpoints."""

  def setUp(self):
    super(TestCommentResource, self).setUp()
    self.api = Api()
    self.client.get("/login")

  @ddt.data(("Creator", 403),
            ("Reader", 403),
            ("Editor", 201),
            ("Administrator", 201))
  @ddt.unpack
  def test_create_global(self, role_name, status_code):
    """Test create comment with {0} permissions via global roles."""
    role = all_models.Role.query.filter(
        all_models.Role.name == role_name
    ).one()
    with factories.single_commit():
      asmt = factories.AssessmentFactory()
      client_user = factories.PersonFactory()
      rbac_factories.UserRoleFactory(role=role, person=client_user)
    asmt_id = asmt.id
    self.api.set_user(client_user)
    self.client.get("/login")
    resp = self.api.post(
        all_models.Comment,
        {"comment": {
            "type": "Comment",
            "description": "<p>comment</p>",
            "related_to": {"type": asmt.type, "id": asmt.id},
            "context": None,
            "send_notification": False,
            "assignee_type": "Verifiers",
        }},
    )
    self.assertEqual(resp.status_code, status_code)
    asmt = all_models.Assessment.query.get(asmt_id)
    if status_code == 201:
      descs = ["<p>comment</p>"]
    else:
      descs = []
    self.assertEqual(descs, [c.description for c in asmt.comments])

  @ddt.data(True, False)
  def test_create_acl(self, update_permissions):
    """Test create comment with permissions via acl read is {0}."""
    role = all_models.Role.query.filter(
        all_models.Role.name == "Creator"
    ).one()
    with factories.single_commit():
      client_user = factories.PersonFactory()
      rbac_factories.UserRoleFactory(role=role, person=client_user)
      acr = factories.AccessControlRoleFactory(
          name="tmp",
          update=update_permissions,
          delete=False,
          read=True,
      )
      asmt = factories.AssessmentFactory()
      factories.AccessControlListFactory(ac_role=acr,
                                         object=asmt,
                                         person=client_user)
    asmt_id = asmt.id
    self.api.set_user(client_user)
    self.client.get("/login")
    resp = self.api.post(
        all_models.Comment,
        {"comment": {
            "type": "Comment",
            "description": "<p>comment</p>",
            "related_to": {"type": asmt.type, "id": asmt.id},
            "context": None,
            "send_notification": False,
            "assignee_type": "Verifiers",
        }},
    )
    self.assertEqual(resp.status_code, 201 if update_permissions else 403)
    asmt = all_models.Assessment.query.get(asmt_id)
    descs = []
    if update_permissions:
      descs.append("<p>comment</p>")
    self.assertEqual(descs, [c.description for c in asmt.comments])
