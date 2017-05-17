# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Test permissions on mapped Document to assessment."""
from ggrc.app import app  # NOQA pylint: disable=unused-import
from ggrc.models import all_models

from integration.ggrc.models import factories
from integration.ggrc import generator
from integration import ggrc

from appengine import base


class BaseTestDocumentPermissions(object):
  """Check permissions for Document instance related to assessment."""

  ROLE = None

  @staticmethod
  def generate_document(**kwargs):
    raise NotImplementedError()

  def setUp(self):
    """Setup test case."""
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
    self.document_id = self.generate_document(link="test.com").id
    self.generator.generate_relationship(
        all_models.Document.query.get(self.document_id),
        self.assessment,
    )
    self.editor = all_models.Person.query.get(self.editor_id)
    self.url_get = self.api.get(all_models.Document, self.document_id)
    self.api.set_user(self.editor)

  def test_get_action_document(self):
    """Test permissions on get."""
    resp = self.api.get(all_models.Document, self.document_id)
    if self.ROLE:
      self.assert200(resp)
    else:
      self.assert403(resp)

  def test_delete_action_document(self):
    """Test permissions on delete."""
    resp = self.api.delete(all_models.Document.query.get(self.document_id))
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
    resp = self.api.put(all_models.Document.query.get(self.document_id), data)
    if self.ROLE:
      self.assert200(resp)
    else:
      self.assert403(resp)


TestUrlEmptyRolePermissions = base.with_memcache(type(
    "TestUrlEmptyRolePermissions",
    (BaseTestDocumentPermissions, ggrc.TestCase),
    {"ROLE": None, "generate_document": factories.UrlFactory}
))

TestUrlCreatorPermissions = base.with_memcache(type(
    "TestUrlCreatorPermissions",
    (BaseTestDocumentPermissions, ggrc.TestCase),
    {"ROLE": "Creator", "generate_document": factories.UrlFactory}
))

TestUrlVerifierPermissions = base.with_memcache(type(
    "TestUrlVerifierPermissions",
    (BaseTestDocumentPermissions, ggrc.TestCase),
    {"ROLE": "Verifier", "generate_document": factories.UrlFactory}
))

TestUrlAssessorPermissions = base.with_memcache(type(
    "TestUrlAssessorPermissions",
    (BaseTestDocumentPermissions, ggrc.TestCase),
    {"ROLE": "Assessor", "generate_document": factories.UrlFactory}
))

TestEvidenceEmptyRolePermissions = base.with_memcache(type(
    "TestEvidenceEmptyRolePermissions",
    (BaseTestDocumentPermissions, ggrc.TestCase),
    {"ROLE": None, "generate_document": factories.EvidenceFactory}
))

TestEvidenceCreatorPermissions = base.with_memcache(type(
    "TestEvidenceCreatorPermissions",
    (BaseTestDocumentPermissions, ggrc.TestCase),
    {"ROLE": "Creator", "generate_document": factories.EvidenceFactory}
))

TestEvidenceVerifierPermissions = base.with_memcache(type(
    "TestEvidenceVerifierPermissions",
    (BaseTestDocumentPermissions, ggrc.TestCase),
    {"ROLE": "Verifier", "generate_document": factories.EvidenceFactory}
))

TestEvidenceAssessorPermissions = base.with_memcache(type(
    "TestEvidenceAssessorPermissions",
    (BaseTestDocumentPermissions, ggrc.TestCase),
    {"ROLE": "Assessor", "generate_document": factories.EvidenceFactory}
))
