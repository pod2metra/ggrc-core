# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""GGRC notification SQLAlchemy layer data model extensions."""

from sqlalchemy.orm import backref

from ggrc import db
from ggrc.models.mixins import Base
from ggrc.models import utils
from ggrc.models import reflection


class NotificationConfig(Base, db.Model):
    __tablename__ = 'notification_configs'
    name = db.Column(db.String, nullable=True)
    enable_flag = db.Column(db.Boolean)
    notif_type = db.Column(db.String)
    person_id = db.Column(
        db.Integer, db.ForeignKey('people.id'), nullable=False)
    person = db.relationship(
        'Person',
        backref=backref('notification_configs', cascade='all, delete-orphan'))

    _api_attrs = reflection.ApiAttributes(
        'person_id',
        'notif_type',
        'enable_flag',
    )

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
    custom_message = db.Column(db.Text, nullable=False, default=u"")
    force_notifications = db.Column(db.Boolean, default=False, nullable=False)
    repeating = db.Column(db.Boolean, nullable=False, default=False)
    notification_type_id = db.Column(
        db.Integer, db.ForeignKey('notification_types.id'), nullable=False)
    notification_type = db.relationship(
        'NotificationType', foreign_keys='Notification.notification_type_id')

    object = utils.PolymorphicRelationship("object_id", "object_type",
                                           "{}_notifiable")
