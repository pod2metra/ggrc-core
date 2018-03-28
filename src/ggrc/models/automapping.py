# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Automapping model"""

from ggrc import db
from ggrc.models.mixins import Base


class Automapping(Base, db.Model):
    """Automapping class

     Used to track which relationship objects were created by an
     automapping even if the base relationship was deleted.
  """
    __tablename__ = 'automappings'
    # relationship_id cannot be a foreign key because of a circular dependency
    relationship_id = db.Column(db.Integer, nullable=True)
    # The fields below are in there in case the original releationship gets
    # deleted
    source_id = db.Column(db.Integer, nullable=False)
    source_type = db.Column(db.String, nullable=False)
    destination_id = db.Column(db.Integer, nullable=False)
    destination_type = db.Column(db.String, nullable=False)

    def __init__(self, parent):
        """Automapping helper"""
        self.source_id = parent.source_id
        self.source_type = parent.source_type
        self.destination_type = parent.destination_type
        self.destination_id = parent.destination_id
