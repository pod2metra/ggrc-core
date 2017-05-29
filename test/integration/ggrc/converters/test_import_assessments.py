# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

# pylint: disable=maybe-no-member, invalid-name

"""Test request import and updates."""

import csv
import datetime

from collections import OrderedDict
from cStringIO import StringIO
from itertools import izip

from flask.json import dumps

from ggrc import db
from ggrc import models
from ggrc.converters import errors

from integration.ggrc.models import factories
from integration.ggrc import TestCase
from integration.ggrc.generator import ObjectGenerator


class TestAssessmentImport(TestCase):
  """Basic Assessment import tests with.

  This test suite should test new Assessment imports, exports, and updates.
  The main focus of these tests is checking error messages for invalid state
  transitions.
  """

  def setUp(self):
    """Set up for Assessment test cases."""
    super(TestAssessmentImport, self).setUp()
    self.client.get("/login")

  def test_import_assessments_with_templates(self):
    """Test importing of assessments with templates."""

    self.import_file("assessment_template_no_warnings.csv")
    response = self.import_file("assessment_with_templates.csv")
    self._check_csv_response(response, {})

    assessment = models.Assessment.query.filter(
        models.Assessment.slug == "A 4").first()

    values = set(v.attribute_value for v in assessment.custom_attribute_values)
    self.assertIn("abc", values)
    self.assertIn("2015-07-15", values)

  def _test_assessment_users(self, asmt, users):
    """ Test that all users have correct roles on specified Assessment"""
    verification_errors = ""
    for user_name, expected_types in users.items():
      try:
        user = models.Person.query.filter_by(name=user_name).first()
        rel = models.Relationship.find_related(asmt, user)
        if expected_types:
          self.assertNotEqual(
              rel, None,
              "User {} is not mapped to {}".format(user.email, asmt.slug))
          self.assertIn("AssigneeType", rel.relationship_attrs)
          self.assertEqual(
              set(rel.relationship_attrs[
                  "AssigneeType"].attr_value.split(",")),
              expected_types
          )
        else:
          self.assertEqual(
              rel, None,
              "User {} is mapped to {}".format(user.email, asmt.slug))
      except AssertionError as error:
        verification_errors += "\n\nChecks for Users-Assessment mapping "\
            "failed for user '{}' with:\n{}".format(user_name, str(error))

    self.assertEqual(verification_errors, "", verification_errors)

  def test_assessment_full_no_warnings(self):
    """ Test full assessment import with no warnings

    CSV sheet:
      https://docs.google.com/spreadsheets/d/1Jg8jum2eQfvR3kZNVYbVKizWIGZXvfqv3yQpo2rIiD8/edit#gid=704933240&vpid=A7
    """
    response = self.import_file("assessment_full_no_warnings.csv")
    self._check_csv_response(response, {})

    # Test first Assessment line in the CSV file
    asmt_1 = models.Assessment.query.filter_by(slug="Assessment 1").first()
    users = {
        "user 1": {"Assessor"},
        "user 2": {"Assessor", "Creator"}
    }
    self._test_assessment_users(asmt_1, users)
    self.assertEqual(asmt_1.status, models.Assessment.START_STATE)

    # Test second Assessment line in the CSV file
    asmt_2 = models.Assessment.query.filter_by(slug="Assessment 2").first()
    users = {
        "user 1": {"Assessor"},
        "user 2": {"Creator"},
        "user 3": {},
        "user 4": {},
        "user 5": {},
    }
    self._test_assessment_users(asmt_2, users)
    self.assertEqual(asmt_2.status, models.Assessment.PROGRESS_STATE)

    audit = [obj for obj in asmt_1.related_objects() if obj.type == "Audit"][0]
    self.assertEqual(audit.context, asmt_1.context)

    evidence = models.Document.query.filter_by(title="some title 2").first()
    self.assertEqual(audit.context, evidence.context)

  def test_assessment_import_states(self):
    """ Test Assessment state imports

    These tests are an intermediate part for zucchini release and will be
    updated in the next release.

    CSV sheet:
      https://docs.google.com/spreadsheets/d/1Jg8jum2eQfvR3kZNVYbVKizWIGZXvfqv3yQpo2rIiD8/edit#gid=299569476
    """
    self.import_file("assessment_full_no_warnings.csv")
    response = self.import_file("assessment_update_intermediate.csv")
    expected_errors = {
        "Assessment": {
            "block_errors": set(),
            "block_warnings": set(),
            "row_errors": set(),
            "row_warnings": set(),
        }
    }
    self._check_csv_response(response, expected_errors)

    assessments = {r.slug: r for r in models.Assessment.query.all()}
    self.assertEqual(assessments["Assessment 60"].status,
                     models.Assessment.START_STATE)
    self.assertEqual(assessments["Assessment 61"].status,
                     models.Assessment.PROGRESS_STATE)
    self.assertEqual(assessments["Assessment 62"].status,
                     models.Assessment.DONE_STATE)
    self.assertEqual(assessments["Assessment 63"].status,
                     models.Assessment.FINAL_STATE)
    self.assertEqual(assessments["Assessment 64"].status,
                     models.Assessment.FINAL_STATE)
    self.assertEqual(assessments["Assessment 3"].status,
                     models.Assessment.FINAL_STATE)
    self.assertEqual(assessments["Assessment 4"].status,
                     models.Assessment.FINAL_STATE)

    # Check that there is only one attachment left
    asmt1 = assessments["Assessment 1"]
    self.assertEqual(len(asmt1.documents), 1)

    # Check that there are only the two new URLs present in asessment 1
    url_titles = set(obj.title for obj in asmt1.related_objects()
                     if isinstance(obj, models.Document))
    self.assertEqual(url_titles, set(["a.b.com", "c d com"]))

  def test_assessment_warnings_errors(self):
    """ Test full assessment import with warnings and errors

    CSV sheet:
      https://docs.google.com/spreadsheets/d/1Jg8jum2eQfvR3kZNVYbVKizWIGZXvfqv3yQpo2rIiD8/edit#gid=889865936
    """
    self.import_file("assessment_full_no_warnings.csv")
    response = self.import_file("assessment_with_warnings_and_errors.csv")

    expected_errors = {
        "Assessment": {
            "block_errors": set([]),
            "block_warnings": {
                errors.UNKNOWN_COLUMN.format(
                    line=2,
                    column_name="error description - non existing column will "
                    "be ignored"
                ),
                errors.UNKNOWN_COLUMN.format(
                    line=2,
                    column_name="actual error message"
                ),
                errors.UNKNOWN_COLUMN.format(
                    line=2,
                    column_name="map:project"
                ),
            },
            "row_errors": {
                errors.MISSING_VALUE_ERROR.format(
                    line=19,
                    column_name="Audit"
                ),
                errors.DUPLICATE_VALUE_IN_CSV.format(
                    line_list="20, 22",
                    column_name="Code",
                    value="Assessment 22",
                    s="",
                    ignore_lines="22",
                ),
            },
            "row_warnings": {
                errors.UNKNOWN_OBJECT.format(
                    line=19,
                    object_type="Audit",
                    slug="not existing"
                ),
                errors.WRONG_VALUE_DEFAULT.format(
                    line=20,
                    column_name="State",
                    value="open",
                ),
            },
        }
    }
    self._check_csv_response(response, expected_errors)

  def test_mapping_control_through_snapshot(self):
    "Test for add mapping control on assessment"
    audit = factories.AuditFactory()
    assessment = factories.AssessmentFactory(audit=audit)
    factories.RelationshipFactory(source=audit, destination=assessment)
    control = factories.ControlFactory()
    revision = models.Revision.query.filter(
        models.Revision.resource_id == control.id,
        models.Revision.resource_type == control.__class__.__name__
    ).order_by(
        models.Revision.id.desc()
    ).first()
    factories.SnapshotFactory(
        parent=audit,
        child_id=control.id,
        child_type=control.__class__.__name__,
        revision_id=revision.id
    )
    db.session.commit()
    self.assertFalse(db.session.query(
        models.Relationship.get_related_query(
            assessment, models.Snapshot()
        ).exists()).first()[0])
    self.import_data(OrderedDict([
        ("object_type", "Assessment"),
        ("Code*", assessment.slug),
        ("map:control", control.slug),
    ]))
    self.assertTrue(db.session.query(
        models.Relationship.get_related_query(
            assessment, models.Snapshot()
        ).exists()).first()[0])

  def test_create_new_assessment_with_mapped_control(self):
    "Test for creation assessment with mapped controls"
    audit = factories.AuditFactory()
    control = factories.ControlFactory()
    revision = models.Revision.query.filter(
        models.Revision.resource_id == control.id,
        models.Revision.resource_type == control.__class__.__name__
    ).order_by(
        models.Revision.id.desc()
    ).first()
    factories.SnapshotFactory(
        parent=audit,
        child_id=control.id,
        child_type=control.__class__.__name__,
        revision_id=revision.id
    )
    db.session.commit()
    self.assertFalse(db.session.query(
        models.Relationship.get_related_query(
            models.Assessment(), models.Snapshot()
        ).exists()).first()[0])
    slug = "TestAssessment"
    self.import_data(OrderedDict([
        ("object_type", "Assessment"),
        ("Code*", slug),
        ("Audit*", audit.slug),
        ("Assignees*", models.Person.query.all()[0].email),
        ("Creators", models.Person.query.all()[0].email),
        ("Title", "Strange title"),
        ("map:control", control.slug),
    ]))
    assessment = models.Assessment.query.filter(
        models.Assessment.slug == slug
    ).first()
    self.assertTrue(db.session.query(models.Relationship.get_related_query(
        assessment, models.Snapshot()).exists()).first()[0]
    )

  def test_create_import_assignee(self):
    "Test for creation assessment with mapped assignees"
    audit = factories.AuditFactory()
    name = "test_name"
    email = "test@email.com"
    assignee_id = factories.PersonFactory(name=name, email=email).id
    slug = "TestAssessment"
    self.import_data(OrderedDict([
        ("object_type", "Assessment"),
        ("Code*", slug),
        ("Audit*", audit.slug),
        ("Assignees*", email),
        ("Creators", models.Person.query.all()[0].email),
        ("Title", "Strange title"),
    ]))
    assessment = models.Assessment.query.filter(
        models.Assessment.slug == slug
    ).first()
    self.assertEqual([assignee_id], [i.id for i in assessment.assessors])

  def test_create_import_creators(self):
    "Test for creation assessment with mapped creator"
    audit = factories.AuditFactory()
    name = "test_name"
    email = "test@email.com"
    creator_id = factories.PersonFactory(name=name, email=email).id
    slug = "TestAssessment"
    self.import_data(OrderedDict([
        ("object_type", "Assessment"),
        ("Code*", slug),
        ("Audit*", audit.slug),
        ("Assignees*", models.Person.query.all()[0].email),
        ("Creators", email),
        ("Title", "Strange title"),
    ]))
    assessment = models.Assessment.query.filter(
        models.Assessment.slug == slug
    ).first()
    self.assertEqual([creator_id], [i.id for i in assessment.creators])

  def test_update_import_creators(self):
    "Test for creation assessment with mapped creator"
    slug = "TestAssessment"
    assessment = factories.AssessmentFactory(slug=slug)
    name = "test_name"
    email = "test@email.com"
    creator_id = factories.PersonFactory(name=name, email=email).id
    self.assertNotEqual([creator_id], [i.id for i in assessment.creators])
    self.import_data(OrderedDict([
        ("object_type", "Assessment"),
        ("Code*", slug),
        ("Creators", email),
    ]))
    assessment = models.Assessment.query.filter(
        models.Assessment.slug == slug
    ).first()
    self.assertEqual([creator_id], [i.id for i in assessment.creators])

  def test_update_import_assignee(self):
    "Test for creation assessment with mapped creator"
    slug = "TestAssessment"
    assessment = factories.AssessmentFactory(slug=slug)
    name = "test_name"
    email = "test@email.com"
    assignee_id = factories.PersonFactory(name=name, email=email).id
    self.assertNotEqual([assignee_id], [i.id for i in assessment.assessors])
    self.import_data(OrderedDict([
        ("object_type", "Assessment"),
        ("Code*", slug),
        ("Assignees", email),
    ]))
    assessment = models.Assessment.query.filter(
        models.Assessment.slug == slug
    ).first()
    self.assertEqual([assignee_id], [i.id for i in assessment.assessors])


class TestAssessmentExport(TestCase):
  """Test Assessment object export."""

  def setUp(self):
    """ Set up for Assessment test cases """
    super(TestAssessmentExport, self).setUp()
    self.client.get("/login")
    self.headers = ObjectGenerator.get_header()

  def export_csv(self, data):
    return self.client.post("/_service/export_csv", data=dumps(data),
                            headers=self.headers)

  def test_simple_export(self):
    """ Test full assessment export with no warnings

    CSV sheet:
      https://docs.google.com/spreadsheets/d/1Jg8jum2eQfvR3kZNVYbVKizWIGZXvfqv3yQpo2rIiD8/edit#gid=704933240&vpid=A7
    """

    self.import_file("assessment_full_no_warnings.csv")
    data = [{
        "object_name": "Assessment",
        "filters": {
            "expression": {}
        },
        "fields": "all",
    }]
    response = self.export_csv(data)
    self.assertIn(u"\u5555", response.data.decode("utf8"))

  def assertColumnExportedValue(self, value, instance, column):
    "Assertion checks is value equal to exported instance column value."
    data = [{
        "object_name": instance.__class__.__name__,
        "fields": "all",
        "filters": {
            "expression": {
                "text": str(instance.id),
                "op": {
                    "name": "text_search",
                }
            },
        },
    }]
    response = self.export_csv(data)

    keys, vals = response.data.strip().split("\n")[9:11]
    keys = next(csv.reader(StringIO(keys), delimiter=","), [])
    vals = next(csv.reader(StringIO(vals), delimiter=","), [])
    instance_dict = dict(izip(keys, vals))

    self.assertEqual(value, instance_dict[column])

  def test_export_assesments_without_map_control(self):
    """Test export assesment without related control instance"""
    audit = factories.AuditFactory()
    assessment = factories.AssessmentFactory(audit=audit)
    factories.RelationshipFactory(source=audit, destination=assessment)
    control = factories.ControlFactory()
    revision = models.Revision.query.filter(
        models.Revision.resource_id == control.id,
        models.Revision.resource_type == control.__class__.__name__
    ).order_by(
        models.Revision.id.desc()
    ).first()
    factories.SnapshotFactory(
        parent=audit,
        child_id=control.id,
        child_type=control.__class__.__name__,
        revision_id=revision.id
    )
    db.session.commit()
    self.assertColumnExportedValue("", assessment, "map:control")

  def test_export_assesments_with_map_control(self):
    """Test export assesment with related control instance

    relation snapshot -> assessment
    """
    audit = factories.AuditFactory()
    assessment = factories.AssessmentFactory(audit=audit)
    factories.RelationshipFactory(source=audit, destination=assessment)
    control = factories.ControlFactory()
    revision = models.Revision.query.filter(
        models.Revision.resource_id == control.id,
        models.Revision.resource_type == control.__class__.__name__
    ).order_by(
        models.Revision.id.desc()
    ).first()
    snapshot = factories.SnapshotFactory(
        parent=audit,
        child_id=control.id,
        child_type=control.__class__.__name__,
        revision_id=revision.id
    )
    db.session.commit()
    factories.RelationshipFactory(source=snapshot, destination=assessment)
    self.assertColumnExportedValue(control.slug, assessment, "map:control")

  def test_export_assesments_with_map_control_mirror_relation(self):
    """Test export assesment with related control instance

    relation assessment -> snapshot
    """
    audit = factories.AuditFactory()
    assessment = factories.AssessmentFactory(audit=audit)
    factories.RelationshipFactory(source=audit, destination=assessment)
    control = factories.ControlFactory()
    revision = models.Revision.query.filter(
        models.Revision.resource_id == control.id,
        models.Revision.resource_type == control.__class__.__name__
    ).order_by(
        models.Revision.id.desc()
    ).first()
    snapshot = factories.SnapshotFactory(
        parent=audit,
        child_id=control.id,
        child_type=control.__class__.__name__,
        revision_id=revision.id
    )
    db.session.commit()
    factories.RelationshipFactory(destination=snapshot, source=assessment)
    self.assertColumnExportedValue(control.slug, assessment, "map:control")

  def test_export_assessments_with_filters_and_conflicting_ca_names(self):
    """Test exporting assessments with conflicting custom attribute names."""
    self.import_file(u"assessment_template_no_warnings.csv")
    self.import_file(u"assessment_with_templates.csv")

    # also create an object level custom attribute with a name that clashes
    # with a name of a "regular" attribute
    assessment = models.Assessment.query.filter(
        models.Assessment.slug == u"A 2").first()
    cad = models.CustomAttributeDefinition(
        attribute_type=u"Text",
        title=u"ca title",
        definition_type=u"assessment",
        definition_id=assessment.id
    )
    db.session.add(cad)
    db.session.commit()

    data = [{
        "object_name": "Assessment",
        "fields": ["slug", "title", "description", "status"],
        "filters": {
            "expression": {
                "left": {
                    "left": "code",
                    "op": {"name": "~"},
                    "right": "A 2"
                },
                "op": {"name": "AND"},
                "right": {
                    "left": "title",
                    "op": {"name": "~"},
                    "right": "no template Assessment"
                }
            },
            "keys": ["code", "title", "status"],
            "order_by": {
                "keys": [],
                "order": "",
                "compare": None
            }
        }
    }]

    response = self.export_csv(data)
    self.assertIn(u"No template Assessment 2", response.data)


class TestAssessmentNotificationOnImport(TestCase):

  default_datetime = datetime.datetime(2017, 1, 1, 12, 20, 31)
  default_person_role = [
      ("creator@example.com", "Creator"),
      ("assessor_1@example.com", "Assessor"),
      ("assessor_2@example.com", "Assessor"),
      ("verifier_1@example.com", "Verifier"),
      ("verifier_2@example.com", "Verifier"),
  ]

  def setUp(self):
    """Set up for Assessment test cases."""
    super(TestAssessmentNotificationOnImport, self).setUp()
    self.client.get("/login")
    self._fix_notification_init()
    self.assessment = self.create_assessment_with_assignees()
    models.Notification.query.delete()

  def _fix_notification_init(self):
    """Fix Notification object init function.

    This is a fix needed for correct created_at field when using freezgun. By
    default the created_at field is left empty and filed by database, which
    uses system time and not the fake date set by freezugun plugin. This fix
    makes sure that object created in freeze_time block has all dates set with
    the correct date and time.
    """
    default_datetime = self.default_datetime

    def init_decorator(init):
      """Wrapper for Notification init function."""

      def new_init(self, *args, **kwargs):
        init(self, *args, **kwargs)
        if hasattr(self, "created_at"):
            self.created_at = default_datetime
      return new_init

    models.Notification.__init__ = init_decorator(models.Notification.__init__)

  @classmethod
  def create_assessment_with_assignees(cls, person_role=None):
    """Create assessment with assignees """
    assessment = factories.AssessmentFactory(
        status=models.Assessment.PROGRESS_STATE
    )
    with factories.single_commit():
      for person, role in person_role or cls.default_person_role:
        person = factories.PersonFactory(email=person)

        object_person_rel = factories.RelationshipFactory(
            source=assessment,
            destination=person
        )

        factories.RelationshipAttrFactory(
            relationship_id=object_person_rel.id,
            attr_name="AssigneeType",
            attr_value=role
        )
    return assessment

  def test_create_noification_on_state_changed(self):
    self.assertEqual(0, len(models.Notification.query.all()))
    self.import_data(OrderedDict([
        ("object_type", "Assessment"),
        ("Code*", self.assessment.slug),
        ("State", self.assessment.FINAL_STATE),
    ]))
    self.assessment = models.Assessment.query.get(self.assessment.id)
    self.assertEqual(self.assessment.FINAL_STATE, self.assessment.status)
    self.assertEqual(1, len(models.Notification.query.all()))

  def test_notification_on_cad_change(self):
    cad = factories.CustomAttributeDefinitionFactory(
        title="test_def",
        definition_type="assessment",
        attribute_type="Text"
    )
    cav_id = factories.CustomAttributeValueFactory(
        custom_attribute=cad,
        attributable=self.assessment,
        attribute_value="test value default"
    ).id
    self.assertEqual(0, len(models.Notification.query.all()))
    self.import_data(OrderedDict([
        ("object_type", "Assessment"),
        ("Code*", self.assessment.slug),
        ("test_def", "new test value"),
    ]))
    cav = models.CustomAttributeValue.query.get(cav_id)
    self.assertEqual("new test value", cav.attribute_value)
    self.assertEqual(1, len(models.Notification.query.all()))
