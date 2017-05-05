# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""GGRC notification SQLAlchemy layer data model extensions."""

import collections
import sqlalchemy as sa
from sqlalchemy.orm import backref
from sqlalchemy.sql import expression

from ggrc import db
from ggrc.models.mixins import Base
from ggrc.models import utils


class NotificationConfig(Base, db.Model):
  __tablename__ = 'notification_configs'
  name = db.Column(db.String, nullable=True)
  enable_flag = db.Column(db.Boolean)
  notif_type = db.Column(db.String)
  person_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
  person = db.relationship(
      'Person',
      backref=backref('notification_configs', cascade='all, delete-orphan'))

  _publish_attrs = [
      'person_id',
      'notif_type',
      'enable_flag',
  ]

  VALID_TYPES = [
      'Email_Now',
      'Email_Digest',
      'Calendar',
  ]


class NotificationType(Base, db.Model):
  __tablename__ = 'notification_types'

  name = db.Column(db.String, nullable=False)
  description = db.Column(db.String, nullable=True)
  advance_notice = db.Column(db.DateTime, nullable=True)
  template = db.Column(db.String, nullable=True)
  instant = db.Column(db.Boolean, nullable=False, default=False)


class Notification(Base, db.Model):
  __tablename__ = 'notifications'

  object_id = db.Column(db.Integer, nullable=False)
  object_type = db.Column(db.String, nullable=False)
  send_on = db.Column(db.DateTime, nullable=False)
  sent_at = db.Column(db.DateTime, nullable=True)
  custom_message = db.Column(db.Text, nullable=True)
  force_notifications = db.Column(db.Boolean, default=False, nullable=False)
  repeating = db.Column(db.Boolean, nullable=False, default=False)
  notification_type_id = db.Column(
      db.Integer, db.ForeignKey('notification_types.id'), nullable=False)
  notification_type = db.relationship(
      'NotificationType', foreign_keys='Notification.notification_type_id')

  object = utils.PolymorphicRelationship("object_id", "object_type",
                                         "{}_notifiable")


def get_notification_type(name):
  from flask import g
  if not hasattr(g, "notification_type_cache"):
    cached_type = collections.namedtuple(
        "CachedType",
        ["id", "name", "description", "advance_notice", "template", "instant"])
    g.notification_type_cache = {}
    for notification in db.session.query(NotificationType):
      g.notification_type_cache[notification.name] = cached_type(
          id=notification.id,
          name=notification.name,
          description=notification.description,
          advance_notice=notification.advance_notice,
          template=notification.template,
          instant=notification.instant
      )
  return g.notification_type_cache[name]


def has_unsent_notifications(obj, notif_type=None):
  """Helper for searching unsent notifications.

  Args:
    notify_type (NotificationType): type of the notifications we're looking
      for.
    obj (sqlalchemy model): Object for which we're looking for notifications.

  Returns:
    True if there are any unsent notifications of notif_type for the given
    object, and False otherwise.
  """
  # check if this notifications exists in db
  query = Notification.query.filter(
      Notification.object_id == obj.id,
      Notification.object_type == obj.type,
      sa.or_(Notification.sent_at.is_(None),
             Notification.repeating == expression.true()),
  )
  if notif_type is not None:
    query = query.filter(Notification.notification_type_id == notif_type.id)
  exists_query = query.exists()
  if db.session.query(exists_query).first()[0]:
    return True
  # check if this notifications created in this session
  for instance in db.session.new:
    if not isinstance(instance, Notification):
      continue
    if notif_type and instance.notification_type_id != notif_type.id:
      continue
    if instance.sent_at is not None:
      continue
    if instance.object_type == obj.type and instance.object_id == obj.id:
      return True
  return False
