# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

from ggrc import db
from ggrc.models.deferred import deferred
from ggrc.models.mixins import Titled, Slugged
from ggrc.models import reflection


class Help(Titled, Slugged, db.Model):
    __tablename__ = 'helps'
    _title_uniqueness = False

    content = deferred(db.Column(db.Text, nullable=False, default=u""), 'Help')

    _fulltext_attrs = [
        'content',
    ]
    _api_attrs = reflection.ApiAttributes('content')
    _sanitize_html = [
        'content',
    ]
