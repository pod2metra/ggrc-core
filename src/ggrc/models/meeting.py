# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

from ggrc import db
from .mixins import Described, Base, Titled
from .object_person import Personable
from ggrc.models import reflection


class Meeting(Titled, Personable, Described, Base, db.Model):
  __tablename__ = 'meetings'
  _title_uniqueness = False

  start_at = db.Column(db.DateTime, nullable=False)
  end_at = db.Column(db.DateTime, nullable=False)

  _api_attrs = reflection.ApiAttributes(
      'start_at',
      'end_at',
      'title',
  )
  _sanitize_html = []

  @classmethod
  def eager_query(cls):
    return super(Meeting, cls).eager_query()
