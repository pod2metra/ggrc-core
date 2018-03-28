# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
""" Model for object_labels association table."""

from ggrc import db
from ggrc.models import utils
from ggrc.models.label import Label
from ggrc.models.mixins import Base


class ObjectLabel(Base, db.Model):
    """ObjectLabel Model."""
    __tablename__ = 'object_labels'

    label_id = db.Column(
        db.Integer, db.ForeignKey(Label.id), nullable=False, primary_key=True)
    object_id = db.Column(db.Integer, nullable=False)
    object_type = db.Column(db.String, nullable=False)

    label = db.relationship(
        'Label',
        primaryjoin='remote(Label.id) == ObjectLabel.label_id',
    )
    labeled_object = utils.PolymorphicRelationship("object_id", "object_type",
                                                   "{}_labeled")

    _extra_table_args = [
        db.UniqueConstraint('label_id', 'object_id', 'object_type'),
    ]
