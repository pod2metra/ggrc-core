# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
""" Tests for ggrc.models.Revision """
import ddt

import ggrc.models
import integration.ggrc.generator
from integration.ggrc import TestCase

from integration.ggrc.models import factories
from integration.ggrc import api_helper


def _get_revisions(obj, field="resource"):
    return ggrc.models.Revision.query.filter_by(
        **{
            field + "_type": obj.__class__.__name__,
            field + "_id": obj.id
        }).all()


def _project_content(content):
    return {
        "source": {
            "type": content["source_type"],
            "id": content["source_id"],
        },
        "destination": {
            "type": content["destination_type"],
            "id": content["destination_id"],
        },
    }


@ddt.ddt
class TestRevisions(TestCase):
    """ Tests for ggrc.models.Revision """

    def setUp(self):
        super(TestRevisions, self).setUp()
        self.gen = integration.ggrc.generator.ObjectGenerator()
        self.api_helper = api_helper.Api()

    def test_revisions(self):
        """ Test revision creation for POST and PUT """
        cls = ggrc.models.DataAsset
        name = cls._inflector.table_singular  # pylint: disable=protected-access
        _, obj = self.gen.generate(
            cls, name, {name: {
                "title": "revisioned v1",
                "context": None,
            }})
        revisions = _get_revisions(obj)
        self.assertEqual(len(revisions), 1)

        _, obj = self.gen.modify(obj, name, {
            name: {
                "slug": obj.slug,
                "title": "revisioned v2",
                "context": None,
            }
        })
        revisions = _get_revisions(obj)
        expected = {("created", "revisioned v1"), ("modified",
                                                   "revisioned v2")}
        actual = {(r.action, r.content["title"]) for r in revisions}
        self.assertEqual(actual, expected)

    def test_relevant_revisions(self):
        """ Test revision creation for mapping to an object """
        cls = ggrc.models.DataAsset
        name = cls._inflector.table_singular  # pylint: disable=protected-access

        _, obj1 = self.gen.generate(
            cls, name, {name: {
                "title": "connected 1",
                "context": None,
            }})

        _, obj2 = self.gen.generate(
            cls, name, {name: {
                "title": "connected 2",
                "context": None,
            }})

        rel_data = {
            "source": {
                "id": obj1.id,
                "type": cls.__name__
            },
            "destination": {
                "id": obj2.id,
                "type": cls.__name__
            },
            "context": None,
        }
        _, rel = self.gen.generate(ggrc.models.Relationship, "relationship",
                                   {"relationship": rel_data})

        revisions_source = _get_revisions(obj1, "source")
        revisions_destination = _get_revisions(obj2, "destination")

        self.assertEqual(revisions_source, revisions_destination)
        self.assertEqual(len(revisions_source), 1)

        self.gen.api.delete(rel)

        revisions_source = _get_revisions(obj1, "source")
        revisions_destination = _get_revisions(obj2, "destination")

        self.assertEqual(revisions_source, revisions_destination)
        self.assertEqual(len(revisions_source), 2)

        expected_data = {
            "source": {
                "type": cls.__name__,
                "id": obj1.id,
            },
            "destination": {
                "type": cls.__name__,
                "id": obj2.id,
            },
        }
        expected = [(u"created", expected_data), ("deleted", expected_data)]

        actual = [(r.action, _project_content(r.content))
                  for r in revisions_source]
        self.assertEqual(sorted(actual), sorted(expected))

    def test_content_length(self):
        """Test revision content length restrictions."""
        process = factories.ProcessFactory(
            title="a" * 200,
            description="b" * 65000,
            notes="c" * 65000,
        )
        revision = ggrc.models.Revision.query.filter(
            ggrc.models.Revision.resource_id == process.id,
            ggrc.models.Revision.resource_type == process.type,
        ).first()
        self.assertIsNotNone(revision)
        self.assertEqual(revision.content["title"], process.title)
        self.assertEqual(revision.content["description"], process.description)

    @ddt.data(True, False)
    def test_revision_after_del_cad(self, is_add_cav):
        """Test creating new revision after deleting CAD.

    In case of deleting CAD, new revision must be created for object,
    which had this CAD.
    """
        with factories.single_commit():
            control = factories.ControlFactory()

            cad = factories.CustomAttributeDefinitionFactory(
                title="test_name",
                definition_type="control",
            )
            if is_add_cav:
                factories.CustomAttributeValueFactory(
                    custom_attribute=cad,
                    attributable=control,
                    attribute_value="text",
                )

            revision_id = ggrc.models.Revision.query.filter(
                ggrc.models.Revision.resource_id == control.id,
                ggrc.models.Revision.resource_type == control.type,
            ).order_by(ggrc.models.Revision.id.desc()).first().id

        self.api_helper.delete(cad)

        control = ggrc.models.Control.query.first()

        last_revision_id = ggrc.models.Revision.query.filter(
            ggrc.models.Revision.resource_id == control.id,
            ggrc.models.Revision.resource_type == control.type,
        ).order_by(ggrc.models.Revision.id.desc()).first().id

        self.assertGreater(last_revision_id, revision_id)

    @ddt.data(True, False)
    def test_change_modified_by(self, is_add_cav):
        """Test checked correct changing of modified_by_id field.

    User 1 create control, user 2 delete CAD. After the deleting CAD
    test checking that modified_by field contains user 2.
    """
        with factories.single_commit():
            control = factories.ControlFactory()
            cad = factories.CustomAttributeDefinitionFactory(
                title="test_cad",
                definition_type="control",
                attribute_type="Text",
            )
            control_id = control.id
            if is_add_cav:
                factories.CustomAttributeValueFactory(
                    custom_attribute=cad,
                    attributable=control,
                    attribute_value="test")

        user = self.gen.generate_person(
            data={"name": "test_admin"}, user_role="Administrator")[1]
        self.api_helper.set_user(user)
        self.client.get("/login")

        control_revisions = ggrc.models.Revision.query.filter(
            ggrc.models.Revision.resource_id == control_id,
            ggrc.models.Revision.resource_type == "Control",
        ).order_by(ggrc.models.Revision.id.desc()).all()
        ids_before_del = set(revision.id for revision in control_revisions)

        cad = ggrc.models.CustomAttributeDefinition.query.filter_by(
            title="test_cad").first()
        resp_delete = self.api_helper.delete(cad)
        self.assert200(resp_delete)
        cad = ggrc.models.CustomAttributeDefinition.query.filter_by(
            title="test_cad").first()
        self.assertIsNone(cad)

        control_revisions_after = ggrc.models.Revision.query.filter(
            ggrc.models.Revision.resource_id == control_id,
            ggrc.models.Revision.resource_type == "Control",
        ).order_by(ggrc.models.Revision.id.desc()).all()
        ids_after_del = set(
            revision.id for revision in control_revisions_after)

        difference_revision_id = ids_after_del.difference(ids_before_del)

        last_revision = ggrc.models.Revision.query.filter(
            ggrc.models.Revision.resource_id == control_id,
            ggrc.models.Revision.resource_type == "Control",
        ).order_by(ggrc.models.Revision.id.desc()).first()

        self.assertSetEqual(difference_revision_id, {last_revision.id})

        expected_id = ggrc.models.Person.query.filter_by(
            name="test_admin").first().id

        self.assertEquals(last_revision.content["modified_by_id"], expected_id)
        self.assertEquals(last_revision.content["modified_by"]["id"],
                          expected_id)
