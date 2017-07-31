# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

from ggrc import db
from ggrc.access_control.roleable import Roleable
from ggrc.fulltext.mixin import Indexed
from .mixins import (BusinessObject, LastDeprecatedTimeboxed,
                     CustomAttributable)
from .object_document import PublicDocumentable
from .object_person import Personable
from .relationship import Relatable
from .track_object_state import HasObjectState


class Facility(Roleable, HasObjectState, PublicDocumentable,
               CustomAttributable, Personable, Relatable,
               LastDeprecatedTimeboxed, BusinessObject, Indexed,
               db.Model):
  __tablename__ = 'facilities'
  _aliases = {
      "document_url": None,
      "document_evidence": None,
  }
