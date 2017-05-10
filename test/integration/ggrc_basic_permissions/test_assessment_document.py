# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Test permissions on mapped Document to assessment."""
from ggrc.app import app  # NOQA pylint: disable=unused-import
from ggrc.models import all_models

from integration.ggrc.models import factories
from integration.ggrc import generator
from integration import ggrc

from appengine import base


@base.with_memcache
class BaseTestDocumentPermissions(ggrc.TestCase):
  """Check permissions for Document instance related to assessment."""

  ROLE = None

  def genarate_relation(self):
    self.generator.generate_relationship(
        all_models.Document.query.get(self.url_id),
        self.assessment,
    )

  def setUp(self):
    super(BaseTestDocumentPermissions, self).setUp()
    self.api = ggrc.api_helper.Api()
    self.generator = generator.ObjectGenerator()
    _, program = self.generator.generate_object(all_models.Program)
    _, audit = self.generator.generate_object(
        all_models.Audit,
        {
            "title": "Audit",
            "program": {"id": program.id},
            "status": "Planned"
        },
    )
    _, self.assessment = self.generator.generate_object(
        all_models.Assessment,
        {
            "title": "Assessment",
            "audit": {"id": audit.id},
            "audit_title": audit.title,
        },
    )
    _, self.editor = self.generator.generate_person(
        user_role="Creator"
    )
    self.editor_id = self.editor.id
    self.assessment = all_models.Assessment.query.get(self.assessment.id)
    self.editor = all_models.Person.query.get(self.editor.id)
    if self.ROLE:
      factories.RelationshipAttrFactory(
          relationship_id=factories.RelationshipFactory(
              source=self.assessment,
              destination=self.editor,
          ).id,
          attr_name="AssigneeType",
          attr_value=self.ROLE
      )
    self.url_id = factories.DocumentFactory(link="test.com").id
    self.genarate_relation()
    self.editor = all_models.Person.query.get(self.editor_id)
    self.url_get = self.api.get(all_models.Document, self.url_id)
    self.api.set_user(self.editor)

  def test_get_action_document(self):
    """Test permissions on get."""
    resp = self.api.get(all_models.Document, self.url_id)
    if self.ROLE:
      self.assert200(resp)
    else:
      self.assert403(resp)

  def test_delete_action_document(self):
    """Test permissions on delete."""
    resp = self.api.delete(all_models.Document.query.get(self.url_id))
    if self.ROLE:
      self.assert200(resp)
    else:
      self.assert403(resp)

  def test_put_action_document(self):
    """Test permissions on put."""
    data = {
        'document': {
            'link': "new_link.com",
            "selfLink": self.url_get.json["document"]["selfLink"],
        }
    }
    resp = self.api.put(all_models.Document.query.get(self.url_id), data)
    if self.ROLE:
      self.assert200(resp)
    else:
      self.assert403(resp)


class BaseTestPermissionsOverObjectDock(BaseTestDocumentPermissions):

  def genarate_relation(self):
    url = all_models.Document.query.get(self.url_id)
    self.generator.generate_object(
        all_models.ObjectDocument,
        data={
            "document": {
                "type": url.type,
                "id": url.id
            },
            "documentable": {
                "type": self.assessment.type,
                "id": self.assessment.id,
            }
        }
    )


class TestCreatorPermissions(BaseTestDocumentPermissions):
  ROLE = "Creator"


class TestVerifierPermissions(BaseTestDocumentPermissions):
  ROLE = "Verifier"


class TestAssessorPermissions(BaseTestDocumentPermissions):
  ROLE = "Assessor"


class TestCreatorPermissionsOverDock(BaseTestPermissionsOverObjectDock):
  ROLE = "Creator"


class TestVerifierPermissionsOverDock(BaseTestPermissionsOverObjectDock):
  ROLE = "Verifier"


class TestAssessorPermissionsOverDock(BaseTestPermissionsOverObjectDock):
  ROLE = "Assessor"
