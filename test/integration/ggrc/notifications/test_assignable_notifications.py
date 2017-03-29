# -*- coding: utf-8 -*-

# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

# pylint: disable=invalid-name

"""Tests for notifications for models with assignable mixin."""

from datetime import datetime
from freezegun import freeze_time
from mock import patch
from sqlalchemy import and_

from ggrc import db
from ggrc.models import Assessment
from ggrc.models import CustomAttributeDefinition
from ggrc.models import CustomAttributeValue
from ggrc.models import Notification
from ggrc.models import NotificationType
from ggrc.models import ObjectDocument
from ggrc.models import Revision
from ggrc.models import Relationship
from integration.ggrc import TestCase
from integration.ggrc import api_helper, generator
from integration.ggrc.models import factories

from integration.ggrc.models.factories import \
    CustomAttributeDefinitionFactory as CAD


class TestAssignableNotification(TestCase):

  """Test setting notifications for assignable mixin."""

  def setUp(self):
    super(TestAssignableNotification, self).setUp()
    self.client.get("/login")
    self._fix_notification_init()
    self.api_helper = api_helper.Api()
    self.objgen = generator.ObjectGenerator()
    factories.AuditFactory(slug="Audit")

  def _fix_notification_init(self):
    """Fix Notification object init function.

    This is a fix needed for correct created_at field when using freezgun. By
    default the created_at field is left empty and filed by database, which
    uses system time and not the fake date set by freezugun plugin. This fix
    makes sure that object created in freeze_time block has all dates set with
    the correct date and time.
    """

    def init_decorator(init):
      """Wrapper for Notification init function."""

      def new_init(self, *args, **kwargs):
        init(self, *args, **kwargs)
        if hasattr(self, "created_at"):
          self.created_at = datetime.now()
      return new_init

    Notification.__init__ = init_decorator(Notification.__init__)

  @classmethod
  def _get_notifications(cls, sent=False, notif_type=None):
    """Get a notification query.

    Args:
      sent (boolean): flag to filter out only notifications that have been
        sent.
      notif_type (string): name of the notification type.

    Returns:
      sqlalchemy query for selected notifications.
    """
    if sent:
      notif_filter = Notification.sent_at.isnot(None)
    else:
      notif_filter = Notification.sent_at.is_(None)

    if notif_type:
      notif_filter = and_(notif_filter, NotificationType.name == notif_type)

    return db.session.query(Notification).join(NotificationType).filter(
        notif_filter
    )

  @patch("ggrc.notifications.common.send_email")
  def test_assessment_without_verifiers(self, _):
    """Test setting notification entries for simple assessments.

    This function tests that each assessment gets an entry in the
    notifications table after it's been created.
    """

    with freeze_time("2015-04-01"):

      self.assertEqual(self._get_notifications().count(), 0)
      self.import_file("assessment_with_templates.csv")
      asmts = {asmt.slug: asmt for asmt in Assessment.query}

      notifications = self._get_notifications().all()
      self.assertEqual(len(notifications), 6)

      revisions = Revision.query.filter(
          Revision.resource_type == 'Notification',
          Revision.resource_id.in_([notif.id for notif in notifications])
      ).count()
      self.assertEqual(revisions, 6)

      self.api_helper.delete(asmts["A 1"])
      self.api_helper.delete(asmts["A 6"])

      self.assertEqual(self._get_notifications().count(), 4)

      self.client.get("/_notifications/send_daily_digest")
      self.assertEqual(self._get_notifications().count(), 0)

  @patch("ggrc.notifications.common.send_email")
  def test_assessment_with_verifiers(self, _):
    """Test notifications entries for declined assessments.

    This tests makes sure there are extra notification entries added when a
    assessment has been declined.
    """
    with freeze_time("2015-04-01"):
      self.assertEqual(self._get_notifications().count(), 0)
      self.import_file("assessment_with_templates.csv")
      asmts = {asmt.slug: asmt for asmt in Assessment.query}

      notifications = self._get_notifications().all()
      self.assertEqual(len(notifications), 6)

      revisions = Revision.query.filter(
          Revision.resource_type == 'Notification',
          Revision.resource_id.in_([notif.id for notif in notifications])
      ).count()
      self.assertEqual(revisions, 6)

      self.client.get("/_notifications/send_daily_digest")
      self.assertEqual(self._get_notifications().count(), 0)

      asmt1 = Assessment.query.get(asmts["A 5"].id)
      # start and finish assessment 1
      self.api_helper.modify_object(asmt1,
                                    {"status": Assessment.PROGRESS_STATE})
      self.assertEqual(self._get_notifications().count(), 0)

      self.api_helper.modify_object(asmt1, {"status": Assessment.DONE_STATE})
      self.assertEqual(self._get_notifications().count(), 1)
      # decline assessment 1
      self.api_helper.modify_object(asmt1,
                                    {"status": Assessment.PROGRESS_STATE})
      self.assertEqual(self._get_notifications().count(), 3)
      self.api_helper.modify_object(asmt1, {"status": Assessment.DONE_STATE})
      self.assertEqual(self._get_notifications().count(), 3)
      # decline assessment 1 the second time
      self.api_helper.modify_object(asmt1,
                                    {"status": Assessment.PROGRESS_STATE})
      self.assertEqual(self._get_notifications().count(), 3)

      asmt6 = Assessment.query.get(asmts["A 6"].id)
      # start and finish assessment 6
      self.api_helper.modify_object(asmt6,
                                    {"status": Assessment.PROGRESS_STATE})
      self.assertEqual(self._get_notifications().count(), 3)
      self.api_helper.modify_object(asmt6, {"status": Assessment.DONE_STATE})
      self.assertEqual(self._get_notifications().count(), 4)
      # decline assessment 6
      self.api_helper.modify_object(asmt6,
                                    {"status": Assessment.PROGRESS_STATE})
      self.assertEqual(self._get_notifications().count(), 6)

      # send all notifications
      self.client.get("/_notifications/send_daily_digest")
      self.assertEqual(self._get_notifications().count(), 0)

      # Refresh the object because of the lost session due to the get call.
      asmt6 = Assessment.query.get(asmts["A 6"].id)
      self.api_helper.modify_object(asmt6,
                                    {"status": Assessment.PROGRESS_STATE})
      self.assertEqual(self._get_notifications().count(), 0)
      self.api_helper.modify_object(asmt6,
                                    {"status": Assessment.DONE_STATE})
      self.assertEqual(self._get_notifications().count(), 1)
      self.api_helper.modify_object(asmt6,
                                    {"status": Assessment.VERIFIED_STATE})
      self.assertEqual(self._get_notifications().count(), 2)
      self.api_helper.modify_object(asmt6,
                                    {"status": Assessment.PROGRESS_STATE})
      self.assertEqual(self._get_notifications().count(), 3)
      # decline assessment 6
      self.api_helper.modify_object(asmt6, {"status": Assessment.DONE_STATE})
      self.assertEqual(self._get_notifications().count(), 3)
      self.api_helper.modify_object(asmt6,
                                    {"status": Assessment.PROGRESS_STATE})
      self.assertEqual(self._get_notifications().count(), 4)

  @patch("ggrc.notifications.common.send_email")
  def test_changing_custom_attributes_triggers_change_notification(self, _):
    """Test that updating Assessment's CA value results in change notification.
    """
    CAD(definition_type="assessment", title="CA 1",)
    cad2 = CAD(definition_type="assessment", title="CA 2",)

    self.import_file("assessment_with_templates.csv")
    asmts = {asmt.slug: asmt for asmt in Assessment.query}

    self.client.get("/_notifications/send_daily_digest")
    self.assertEqual(self._get_notifications().count(), 0)

    # set initial CA value on the Assessment (also to put it into "In Progress"
    cad2 = CustomAttributeDefinition.query.filter(
        CustomAttributeDefinition.title == "CA 2").one()
    val2 = CustomAttributeValue(attribute_value="1a2b3", custom_attribute=cad2)

    asmt4 = Assessment.query.get(asmts["A 4"].id)
    self.api_helper.modify_object(
        asmt4,
        {
            "custom_attribute_values": [{
                "attributable_id": asmt4.id,
                "attributable_type": "Assessment",
                "id": val2.id,
                "custom_attribute_id": cad2.id,
                "attribute_value": val2.attribute_value,
            }]
        }
    )

    # there should still be no notifications...
    self.assertEqual(
        self._get_notifications(notif_type="assessment_updated").count(), 0)

    # now change the CA value and check if notification gets generated
    cad2 = CustomAttributeDefinition.query.filter(
        CustomAttributeDefinition.title == "CA 2").one()
    val2 = CustomAttributeValue(attribute_value="NEW", custom_attribute=cad2)

    asmt4 = Assessment.query.get(asmts["A 4"].id)
    self.api_helper.modify_object(
        asmt4,
        {
            "custom_attribute_values": [{
                "attributable_id": asmt4.id,
                "attributable_type": "Assessment",
                "custom_attribute_id": cad2.id,
                "id": val2.id,
                "attribute_value": val2.attribute_value,
            }]
        }
    )

    notifs = self._get_notifications(notif_type="assessment_updated").all()
    self.assertEqual(len(notifs), 1)

  @patch("ggrc.notifications.common.send_email")
  def test_directly_completing_assessments(self, _):
    """Test that immediately finishing an Assessment produces a notification.

    "Immediately" here means directly sending an Assessment to either the
    "Completed", or the "Ready for Review" state, skipping the "In Progress"
    state.
    """
    self.import_file("assessment_with_templates.csv")
    asmts = {asmt.slug: asmt for asmt in Assessment.query}

    self.client.get("/_notifications/send_daily_digest")
    self.assertEqual(self._get_notifications().count(), 0)

    # directly sending an Assessment to the "Ready for Review" state
    asmt4 = Assessment.query.get(asmts["A 4"].id)
    self.api_helper.modify_object(asmt4,
                                  {"status": Assessment.DONE_STATE})
    self.assertEqual(self._get_notifications().count(), 1)

    # clear notifications
    self.client.get("/_notifications/send_daily_digest")
    self.assertEqual(self._get_notifications().count(), 0)

    # directly sending an Assessment to the "Completed" state
    asmt5 = Assessment.query.get(asmts["A 5"].id)
    self.api_helper.modify_object(asmt5,
                                  {"status": Assessment.FINAL_STATE})
    self.assertEqual(self._get_notifications().count(), 1)

  @patch("ggrc.notifications.common.send_email")
  def test_changing_assigned_people_triggers_notifications(self, _):
    """Test that changing Assessment people results in change notification.

    Adding (removing) a person to (from) Assessment should be detected and
    considered an Assessment change.
    """
    self.import_file("assessment_with_templates.csv")
    asmts = {asmt.slug: asmt for asmt in Assessment.query}

    self.client.get("/_notifications/send_daily_digest")
    self.assertEqual(self._get_notifications().count(), 0)

    asmt = Assessment.query.get(asmts["A 5"].id)

    # add an Assessor, there should be no notifications because the Assessment
    # has not been started yet
    person = factories.PersonFactory()
    response, relationship = self.objgen.generate_relationship(
        person, asmt, attrs={"AssigneeType": "Assessor"})
    self.assertEqual(response.status_code, 201)

    change_notifs = self._get_notifications(notif_type="assessment_updated")
    self.assertEqual(change_notifs.count(), 0)
    asmt = Assessment.query.get(asmts["A 5"].id)

    # move Assessment to to "In Progress" state and clear notifications
    self.api_helper.modify_object(
        asmt, {"status": Assessment.PROGRESS_STATE})

    self.client.get("/_notifications/send_daily_digest")
    self.assertEqual(self._get_notifications().count(), 0)
    asmt = Assessment.query.get(asmts["A 5"].id)

    # assign another Assignee, change notification should be created
    person2 = factories.PersonFactory()
    response, relationship2 = self.objgen.generate_relationship(
        person2, asmt, attrs={"AssigneeType": "Assessor"})
    self.assertEqual(response.status_code, 201)
    rel2_id = relationship2.id

    change_notifs = self._get_notifications(notif_type="assessment_updated")
    self.assertEqual(change_notifs.count(), 1)

    # clear notifications, assign the same person as Verfier, check for
    # change notification
    self.client.get("/_notifications/send_daily_digest")
    self.assertEqual(change_notifs.count(), 0)
    asmt = Assessment.query.get(asmts["A 5"].id)
    relationship2 = Relationship.query.get(rel2_id)

    self.api_helper.modify_object(
        relationship2, {"AssigneeType": "Assessor,Verifier"})

    change_notifs = self._get_notifications(notif_type="assessment_updated")
    self.assertEqual(change_notifs.count(), 1)

    # clear notifications, delete an Assignee, test for change notification
    self.client.get("/_notifications/send_daily_digest")
    self.assertEqual(change_notifs.count(), 0)
    asmt = Assessment.query.get(asmts["A 5"].id)

    self.api_helper.delete(relationship)

    change_notifs = self._get_notifications(notif_type="assessment_updated")
    self.assertEqual(change_notifs.count(), 1)

    # clear notifications, delete one of the person's roles, test for
    # change notification
    self.client.get("/_notifications/send_daily_digest")
    self.assertEqual(change_notifs.count(), 0)
    asmt = Assessment.query.get(asmts["A 5"].id)
    relationship2 = Relationship.query.get(rel2_id)

    self.api_helper.modify_object(
        relationship2, {"AssigneeType": "Assessor"})  # not Verifier anymore

    change_notifs = self._get_notifications(notif_type="assessment_updated")
    self.assertEqual(change_notifs.count(), 1)

    # changing people if completed should result in "reopened" notification

    # TODO: contrary to how relations to Documents behave, assigning a Person
    # to an Assessment causes the latter to be immediately moved to the
    # "In Progress" state, making the relationship change handler to think that
    # the Assessment was modified in the "In Progress" state, resulting in
    # a missing assessment_reopened notification. We thus skip this check for
    # the time being.

    # asmt = Assessment.query.get(asmts["A 5"].id)
    # self.api_helper.modify_object(
    #     asmt, {"status": Assessment.FINAL_STATE})
    # self.client.get("/_notifications/send_daily_digest")
    # self.assertEqual(self._get_notifications().count(), 0)
    # asmt = Assessment.query.get(asmts["A 5"].id)

    # person = factories.PersonFactory()
    # response, relationship = self.objgen.generate_relationship(
    #     person, asmt, attrs={"AssigneeType": "Assessor"})
    # self.assertEqual(response.status_code, 201)

    # reopened_notifs = self._get_notifications(
    #     notif_type="assessment_reopened")
    # self.assertEqual(reopened_notifs.count(), 1)

  @patch("ggrc.notifications.common.send_email")
  def test_changing_assessment_urls_triggers_notifications(self, _):
    """Test that changing Assessment URLs results in change notification.

    Adding (removing) a URL to (from) Assessment should be detected and
    considered an Assessment change.
    """
    self.import_file("assessment_with_templates.csv")
    asmts = {asmt.slug: asmt for asmt in Assessment.query}

    self.client.get("/_notifications/send_daily_digest")
    self.assertEqual(self._get_notifications().count(), 0)

    asmt = Assessment.query.get(asmts["A 5"].id)

    # add a URL, there should be no notifications because the Assessment
    # has not been started yet
    url = factories.DocumentFactory(link="www.foo.com")
    response, relationship = self.objgen.generate_relationship(url, asmt)
    self.assertEqual(response.status_code, 201)

    change_notifs = self._get_notifications(notif_type="assessment_updated")
    self.assertEqual(change_notifs.count(), 0)
    asmt = Assessment.query.get(asmts["A 5"].id)

    # move Assessment to to "In Progress" state and clear notifications
    self.api_helper.modify_object(
        asmt, {"status": Assessment.PROGRESS_STATE})

    self.client.get("/_notifications/send_daily_digest")
    self.assertEqual(self._get_notifications().count(), 0)
    asmt = Assessment.query.get(asmts["A 5"].id)

    # add another URL, change notification should be created
    url2 = factories.DocumentFactory(link="www.bar.com")
    response, _ = self.objgen.generate_relationship(url2, asmt)
    self.assertEqual(response.status_code, 201)

    change_notifs = self._get_notifications(notif_type="assessment_updated")
    self.assertEqual(change_notifs.count(), 1)

    # clear notifications, delete a URL, test for change notification
    self.client.get("/_notifications/send_daily_digest")
    self.assertEqual(change_notifs.count(), 0)
    asmt = Assessment.query.get(asmts["A 5"].id)

    self.api_helper.delete(relationship)

    change_notifs = self._get_notifications(notif_type="assessment_updated")
    self.assertEqual(change_notifs.count(), 1)

    # changing URLs if completed should result in "reopened" notification
    asmt = Assessment.query.get(asmts["A 5"].id)
    self.api_helper.modify_object(
        asmt, {"status": Assessment.FINAL_STATE})
    self.client.get("/_notifications/send_daily_digest")
    self.assertEqual(self._get_notifications().count(), 0)
    asmt = Assessment.query.get(asmts["A 5"].id)

    url = factories.DocumentFactory(link="www.abc.com")
    response, relationship = self.objgen.generate_relationship(url, asmt)
    self.assertEqual(response.status_code, 201)

    reopened_notifs = self._get_notifications(notif_type="assessment_reopened")
    self.assertEqual(reopened_notifs.count(), 1)

  @patch("ggrc.notifications.common.send_email")
  def test_changing_assessment_attachment_triggers_notifications(self, _):
    """Test that changing Assessment attachment results in change notification.

    Adding (removing) an attachment to (from) Assessment should be detected and
    considered an Assessment change.
    """
    self.import_file("assessment_with_templates.csv")
    asmts = {asmt.slug: asmt for asmt in Assessment.query}

    self.client.get("/_notifications/send_daily_digest")
    self.assertEqual(self._get_notifications().count(), 0)

    asmt = Assessment.query.get(asmts["A 5"].id)

    # add an attachment, there should be no notifications because the
    # Assessment has not been started yet
    pdf_doc = factories.DocumentFactory(title="foo.pdf")
    data = {
        "document": {"type": pdf_doc.type, "id": pdf_doc.id},
        "documentable": {"type": asmt.type, "id": asmt.id}
    }
    response, obj_doc = self.objgen.generate_object(ObjectDocument, data=data)
    self.assertEqual(response.status_code, 201)

    change_notifs = self._get_notifications(notif_type="assessment_updated")
    self.assertEqual(change_notifs.count(), 0)
    asmt = Assessment.query.get(asmts["A 5"].id)

    # move Assessment to to "In Progress" state and clear notifications
    self.api_helper.modify_object(
        asmt, {"status": Assessment.PROGRESS_STATE})

    self.client.get("/_notifications/send_daily_digest")
    self.assertEqual(self._get_notifications().count(), 0)
    asmt = Assessment.query.get(asmts["A 5"].id)

    # attach another document, change notification should be created
    image = factories.DocumentFactory(link="foobar.png")
    data = {
        "document": {"type": image.type, "id": image.id},
        "documentable": {"type": asmt.type, "id": asmt.id}
    }
    response, _ = self.objgen.generate_object(ObjectDocument, data=data)
    self.assertEqual(response.status_code, 201)

    change_notifs = self._get_notifications(notif_type="assessment_updated")
    self.assertEqual(change_notifs.count(), 1)

    # clear notifications, remove an attachment, test for change notification
    self.client.get("/_notifications/send_daily_digest")
    self.assertEqual(change_notifs.count(), 0)
    asmt = Assessment.query.get(asmts["A 5"].id)

    self.api_helper.delete(obj_doc)

    change_notifs = self._get_notifications(notif_type="assessment_updated")
    self.assertEqual(change_notifs.count(), 1)

    # changing attachments completed should result in "reopened" notification
    asmt = Assessment.query.get(asmts["A 5"].id)
    self.api_helper.modify_object(
        asmt, {"status": Assessment.FINAL_STATE})
    self.client.get("/_notifications/send_daily_digest")
    self.assertEqual(self._get_notifications().count(), 0)
    asmt = Assessment.query.get(asmts["A 5"].id)

    file_foo = factories.DocumentFactory(link="foo.txt")
    data = {
        "document": {"type": file_foo.type, "id": file_foo.id},
        "documentable": {"type": asmt.type, "id": asmt.id}
    }
    response, _ = self.objgen.generate_object(ObjectDocument, data=data)
    self.assertEqual(response.status_code, 201)

    reopened_notifs = self._get_notifications(notif_type="assessment_reopened")
    self.assertEqual(reopened_notifs.count(), 1)
