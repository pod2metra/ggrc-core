# -*- coding: utf-8 -*-

# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Notification handlers for object in the ggrc module.

This module contains all function needed for handling notification objects
needed by ggrc notifications.
"""

# pylint: disable=too-few-public-methods

from itertools import chain
from collections import namedtuple
from datetime import date
from functools import partial
from numbers import Number
from operator import attrgetter

from enum import Enum

from sqlalchemy import inspect
from sqlalchemy import event

from ggrc import db
from ggrc import models
from ggrc.models.notification import (
    get_notification_type,
    has_unsent_notifications,
)
from ggrc.models.mixins.statusable import Statusable


class Transitions(Enum):
  """Assesment state transitions names."""
  TO_COMPLETED = "assessment_completed"
  TO_REVIEW = "assessment_ready_for_review"
  TO_VERIFIED = "assessment_verified"
  TO_REOPENED = "assessment_reopened"


IdValPair = namedtuple("IdValPair", ["id", "val"])


def _add_notification(obj, notif_type, when=None):
  """Add notification for an object.

  Args:
    obj (Model): an object for which we want te add a notification.
    notif_type (NotificationType): type of notification that we want to store.
    when (datetime): date and time when we want the notification to be sent.
      default value is now.
  """
  if not notif_type:
    return
  if not when:
    when = date.today()
  db.session.add(models.Notification(
      object=obj,
      send_on=when,
      notification_type_id=notif_type.id,
  ))


def _add_assignable_declined_notif(obj):
  """Add entries for assignable declined notifications.

  Args:
    obj (Assignable): Any object with assignable mixin for which we want to add
      notifications.
  """
  # pylint: disable=protected-access
  name = "{}_declined".format(obj._inflector.table_singular)
  notif_type = get_notification_type(name)

  if not has_unsent_notifications(obj, notif_type):
    _add_notification(obj, notif_type)


def _add_assessment_updated_notif(obj):
  """Add a notification record on the change of an object.

  If the same notification type for the object already exists and has not been
  sent yet, do not do anything.

  Args:
    obj (models.mixins.Assignable): an object for which to add a notification
  """
  notif_type = get_notification_type("assessment_updated")
  if not has_unsent_notifications(obj, notif_type):
    _add_notification(obj, notif_type)


def _add_state_change_notif(obj, state_change):
  """Add a notification record on changing the given object's status.

  If the same notification type for the object already exists and has not been
  sent yet, do not do anything.

  Args:
    obj (models.mixins.Assignable): an object for which to add a notification
    state_change (Transitions): the state transition that has happened
  """
  notif_type = get_notification_type(state_change.value)

  if not has_unsent_notifications(obj, notif_type):
    _add_notification(obj, notif_type)


def handle_assignable_modified(obj):
  """A handler for the Assignable object modified event.

  Args:
    obj (models.mixins.Assignable): an object that has been modified
  """
  handle_reminder(obj)
  attrs = inspect(obj).attrs

  status_history = attrs["status"].history

  old_state = status_history.deleted[0] if status_history.deleted else None
  new_state = status_history.added[0] if status_history.added else None

  # The transition from "ready to review" to "in progress" happens when an
  # object is declined, so this is used as a triger for declined notifications.
  if (old_state == Statusable.DONE_STATE and
     new_state == Statusable.PROGRESS_STATE):
    _add_assignable_declined_notif(obj)

  transitions_map = {
      (Statusable.START_STATE, Statusable.FINAL_STATE):
          Transitions.TO_COMPLETED,
      (Statusable.START_STATE, Statusable.DONE_STATE):
          Transitions.TO_REVIEW,
      (Statusable.PROGRESS_STATE, Statusable.FINAL_STATE):
          Transitions.TO_COMPLETED,
      (Statusable.PROGRESS_STATE, Statusable.DONE_STATE):
          Transitions.TO_REVIEW,
      (Statusable.DONE_STATE, Statusable.FINAL_STATE):
          Transitions.TO_VERIFIED,
      (Statusable.FINAL_STATE, Statusable.PROGRESS_STATE):
          Transitions.TO_REOPENED,
      (Statusable.DONE_STATE, Statusable.PROGRESS_STATE):
          Transitions.TO_REOPENED,
  }
  state_change = transitions_map.get((old_state, new_state))
  if state_change:
    _add_state_change_notif(obj, state_change)
  # no interest in modifications when an assignable object is not ative yet
  if obj.status == Statusable.START_STATE:
    return

  # changes of some of the attributes are not considered as a modification of
  # the obj itself, e.g. metadata not editable by the end user, or changes
  # covered by other event types such as "comment created"
  # pylint: disable=invalid-name
  IGNORE_ATTRS = frozenset((
      u"_notifications", u"comments", u"context", u"context_id", u"created_at",
      u"custom_attribute_definitions", u"custom_attribute_values",
      u"_custom_attribute_values", u"finished_date", u"id", u"modified_by",
      u"modified_by_id", u"object_level_definitions", u"os_state",
      u"related_destinations", u"related_sources", u"status",
      u"task_group_objects", u"updated_at", u"verified_date",
  ))

  is_changed = False

  for attr_name, val in attrs.items():
    if attr_name in IGNORE_ATTRS:
      continue

    if val.history.has_changes():
      # the exact order of recipients in the string does not matter, hence the
      # need for an extra check
      if attr_name == u"recipients" and not _recipients_changed(val.history):
        continue
      is_changed = True
      break
  is_changed = is_changed or _ca_values_changed(obj)  # CA check only if needed

  if not is_changed:
    return  # no changes detected, nothing left to do

  _add_assessment_updated_notif(obj)

  # When modified, a done Assessment gets automatically reopened, but that is
  # not directly observable via status change history, thus an extra check.
  if obj.status in Statusable.DONE_STATES:
    _add_state_change_notif(obj, Transitions.TO_REOPENED)


def _ca_values_changed(obj):
  """Check if object's custom attribute values have been changed.

  The changes are determined by comparing the current object custom attributes
  with the CA values from object's last known revision. If the latter does not
  exist, it is considered that there are no changes - since the object has
  apparently just been created.

  Args:
    obj (models.mixins.Assignable): the object to check

  Returns:
    (bool) True if there is a change to any of the CA values, False otherwise.
  """
  def stringify_if_number(val):
    """Convert a maybe-number to a string so that e.g. u"1" will match 1."""
    if isinstance(val, bool):
      return val
    return str(val) if isinstance(val, Number) else val

  rev = db.session.query(models.Revision) \
                  .filter_by(resource_id=obj.id, resource_type=obj.type) \
                  .order_by(models.Revision.id.desc()) \
                  .first()
  old_cavs = rev.content.get("custom_attribute_values", []) if rev else []
  new_cavs = getattr(obj, "custom_attribute_values", [])

  # It can happen that CAV objects have no IDs - we ignore those, as those
  # cannot be considered "changed".
  old_cavs = (IdValPair(cav["id"], cav["attribute_value"]) for cav in old_cavs
              if cav["id"] is not None)
  new_cavs = (IdValPair(cav.id, cav.attribute_value) for cav in new_cavs
              if cav.id is not None)

  for old, new in _align_by_ids(old_cavs, new_cavs):
    # one of the items is None only in an (unlikely) scenario when a CA was
    # added/removed - we do not consider that as a CA value change
    if old is None or new is None:
      continue

    old_val = stringify_if_number(old.val)
    new_val = stringify_if_number(new.val)
    if old_val != new_val:
      return True

  return False


def _align_by_ids(items, items2):
  """Generate pairs of items from both iterables, matching them by IDs.

  The items within each iterable must have a unique id attribute (with a value
  other than None). If an item from one iterable does not have a matching item
  in the other, None is used for the missing item.

  Args:
    items: The first iterable.
    items2: The second iterable.

  Yields:
    Pairs of items with matching IDs (one of the items can be None).
  """
  STOP = Ellipsis  # iteration sentinel alias  # pylint: disable=invalid-name

  sort_by_id = partial(sorted, key=attrgetter("id"))
  items = chain(sort_by_id(items), [STOP])
  items2 = chain(sort_by_id(items2), [STOP])

  first, second = next(items), next(items2)

  while first is not STOP or second is not STOP:
    min_id = min(pair.id for pair in (first, second) if pair is not STOP)
    id_one, id_two = getattr(first, "id", None), getattr(second, "id", None)

    yield (first if id_one == min_id else None,
           second if id_two == min_id else None)

    if id_one == min_id:
      first = next(items)
    if id_two == min_id:
      second = next(items2)


def _recipients_changed(history):
  """Check if the recipients attribute has been semantically modified.

  The recipients attribute is a comma-separated string, and the exact order of
  the items in it does not matter, i.e. it is not considered a change.

  Args:
    history (sqlalchemy.orm.attributes.History): recipients' value history

  Returns:
    True if there was a (semantic) change, False otherwise
  """
  old_val = history.deleted[0] if history.deleted else ""
  new_val = history.added[0] if history.added else ""

  if old_val is None:
    old_val = ""

  if new_val is None:
    new_val = ""

  return sorted(old_val.split(",")) != sorted(new_val.split(","))


def handle_assignable_created(obj):
  name = "{}_open".format(obj._inflector.table_singular)
  notif_type = get_notification_type(name=name)
  _add_notification(obj, notif_type)


def handle_assignable_deleted(obj):
  models.Notification.query.filter(
      models.Notification.object_id == obj.id,
      models.Notification.object_type == obj.type,
  ).delete()

  models.Notification.query.filter(
      models.Notification.object_id == 0,
      models.Notification.object_type == obj.type,
  ).delete()


def handle_reminder(obj):
  """Handles reminders for an object

  Args:
    obj: Object to process
    reminder_type: Reminder handler to use for processing event
    """
  if obj.reminderType in obj.REMINDERABLE_HANDLERS:
    reminder_settings = obj.REMINDERABLE_HANDLERS[obj.reminderType]
    handler = reminder_settings['handler']
    data = reminder_settings['data']
    handler(obj, data)


def handle_comment_created(obj):
  """Add notification entries for new comments.

  Args:
    obj (Comment): New comment.
  """
  if obj.send_notification:
    notif_type = get_notification_type("comment_created")
    _add_notification(obj, notif_type)


def handle_relationship_altered(rel):
  """Handle creation or deletion of a relationship between two objects.

  Relationships not involving an Assessment are ignored. For others, if a
  Person or a Document is assigned/attached (or removed from) an Assessment,
  that is considered an Assessment modification and hence a notification is
  created (unless the Assessment has not been started yet, of course).

  Args:
    rel (Relationship): Created (or deleted) relationship instance.
  """
  if rel.source_type != u"Assessment" != rel.destination_type:
    return
  if rel.source_type == "Assessment":
    asmt = db.session.query(models.Assessment).get(rel.source_id)
    other_type = rel.destination_type
  else:
    asmt = db.session.query(models.Assessment).get(rel.destination_id)
    other_type = rel.source_type
  if other_type not in (u"Document", u"Person"):
    return
  if asmt.status != Statusable.START_STATE:
    _add_assessment_updated_notif(asmt)

  # when modified, a done Assessment gets automatically reopened
  if asmt.status in Statusable.DONE_STATES:
    _add_state_change_notif(asmt, Transitions.TO_REOPENED)


def handle_attachment_altered(rel):
  """Handle attaching or detaching a document to an object.

  If the object the attachments were altered for is an Assesment, a change
  notification is created (unless the Assessment has not been started yet).

  Args:
    rel (ObjectDocument): an object describing the attachment relationship
  """
  if rel.documentable_type != u"Assessment":
    return

  asmt = db.session.query(models.Assessment).get(rel.documentable_id)
  if asmt.status != Statusable.START_STATE:
    _add_assessment_updated_notif(asmt)

  # when modified, a done Assessment gets automatically reopened
  if asmt.status in Statusable.DONE_STATES:
    _add_state_change_notif(asmt, Transitions.TO_REOPENED)


def register_handlers():  # noqa: C901
  """Register listeners for notification handlers."""

  new_handlers = {
      models.Assessment: handle_assignable_created,
      models.Comment: handle_comment_created,
      models.Relationship: handle_relationship_altered,
      models.ObjectDocument: handle_attachment_altered,
  }
  delete_handlers = {
      models.Assessment: handle_assignable_deleted,
      models.Relationship: handle_relationship_altered,
      models.ObjectDocument: handle_attachment_altered,
  }
  update_handlers = {
      models.Assessment: handle_assignable_modified,
      models.Relationship: handle_relationship_altered,
      models.ObjectDocument: handle_attachment_altered,
  }

  @event.listens_for(db.session.__class__, 'after_flush')
  def after_flush_handler(session, flush_context):
    for instance in session.new:
      if instance.__class__ in new_handlers:
        new_handlers[instance.__class__](instance)
    for instance in session.deleted:
      if instance.__class__ in delete_handlers:
        delete_handlers[instance.__class__](instance)
    for instance in session.dirty:
      if isinstance(instance, models.CustomAttributeValue):
        instance = instance.attributable
      if instance.__class__ in update_handlers:
        update_handlers[instance.__class__](instance)
