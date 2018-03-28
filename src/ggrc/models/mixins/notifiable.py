# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Module containing Notifiable mixin.

The mixin is used primarily to create backrefs in Notification model.
"""

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr


class Notifiable(object):
    """Notifiable mixin.

  Defines a backref in Notification model named like ModelName_notifiable.
  """
    # pylint: disable=too-few-public-methods

    @declared_attr
    def _notifications(cls):  # pylint: disable=no-self-argument
        """Relationship with notifications for cls."""
        from ggrc.models.notification import Notification

        def join_function():
            """Object and Notification join function."""
            object_id = sa.orm.foreign(Notification.object_id)
            object_type = sa.orm.foreign(Notification.object_type)
            return sa.and_(object_type == cls.__name__, object_id == cls.id)

        return sa.orm.relationship(
            Notification,
            primaryjoin=join_function,
            backref="{}_notifiable".format(cls.__name__),
        )
