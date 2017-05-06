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
class BaseTestObjectFolderPermissions(ggrc.TestCase):
  """Check permissions for ObjectFolder instance related to assessment."""

  ROLE = None

  def setUp(self):
    super(BaseTestObjectFolderPermissions, self).setUp()
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
    if self.ROLE:
      factories.RelationshipAttrFactory(
          relationship_id=factories.RelationshipFactory(
              source=self.assessment,
              destination=self.editor,
          ).id,
          attr_name="AssigneeType",
          attr_value=self.ROLE
      )
    self.folder_id = factories.FolderFactory(
        folder_id="test folder id",
        folderable=audit,
    ).id
    self.editor = all_models.Person.query.get(self.editor_id)
    self.folder_get = self.api.get(all_models.ObjectFolder, self.folder_id)
    self.api.set_user(self.editor)

  def test_get_action_document(self):
    """Test permissions on get."""
    resp = self.api.get(all_models.ObjectFolder, self.folder_id)
    if self.ROLE:
      self.assert200(resp)
    else:
      self.assert403(resp)

  def test_delete_action_document(self):
    """Test permissions on delete."""
    resp = self.api.delete(all_models.ObjectFolder.query.get(self.folder_id))
    self.assert403(resp)

  def test_put_action_document(self):
    """Test permissions on put."""
    data = {
        'object_folder': {
            'folder_id': "bla bla",
            "selfLink": self.folder_get.json["object_folder"]["selfLink"],
        }
    }
    resp = self.api.put(all_models.ObjectFolder.query.get(self.folder_id),
                        data)
    self.assert403(resp)


class TestCreatorObjectFolderPermisssions(BaseTestObjectFolderPermissions):
  ROLE = "Creator"


class TestVerifierObjectFolderPermisssions(BaseTestObjectFolderPermissions):
  ROLE = "Verifier"


class TestAssessorObjectFolderPermisssions(BaseTestObjectFolderPermissions):
  ROLE = "Assessor"
