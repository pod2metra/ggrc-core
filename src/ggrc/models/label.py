# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Module containing Document model."""

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr

from ggrc import db
from ggrc.models import mixins
from ggrc.models import reflection

from ggrc.fulltext import mixin as ft_mixin
from ggrc.fulltext import attributes


class Label(ft_mixin.Indexed, mixins.Base, db.Model):
  """Lable model

  Model holds all labels in the application.
  """

  __tablename__ = 'labels'
  name = db.Column(db.String, nullable=False)
  object_type = db.Column(db.String)

  @staticmethod
  def _extra_table_args(_):
    return (
        db.UniqueConstraint('name', 'object_type'),
    )


class ObjectLabelRelation(mixins.Base, db.Model):
  """ObjectLabelRelation model

  Model holds realtions between object and label.
  """
  __tablename__ = 'object_label_relations'
  object_id = db.Column(db.Integer, nullable=False)
  object_type = db.Column(db.String, nullable=False)
  label_id = db.Column(db.Integer, db.ForeignKey("labels.id"), nullable=False)

  @property
  def object_attr(self):
    return '{0}_object'.format(self.object_type)

  @property
  def object(self):
    return getattr(self, self.object_attr)

  @object.setter
  def object(self, value):
    self.object_id = getattr(value, 'id', None)
    self.object_type = getattr(value, 'type', None)
    return setattr(self, self.object_attr, value)

  @staticmethod
  def _extra_table_args(_):
    return (
        db.UniqueConstraint('label_id', 'object_id', 'object_type'),
        db.Index('idx_object_type_object_idx', 'object_type', 'object_id'),
    )


class Labeled(object):
  _update_raw = ['labels', ]
  _api_attrs = reflection.ApiAttributes(*_include_links)
  _fulltext_attrs = [attributes.MultipleSubpropertyFullTextAttr('label',
                                                                'labels',
                                                                ["name"])]

  @declared_attr
  def _labels(cls):  # pylint: disable=no-self-argument
    return db.relationship(
        Label,
        primaryjoin=lambda: (
            Label.id == sa.orm.remote(ObjectLabelRelation.label_id)
        ),
        secondary=ObjectLabelRelation.__table__,
        secondaryjoin=lambda: sa.and_(
            sa.orm.remote(ObjectLabelRelation.object_id) == cls.id,
            sa.orm.remote(ObjectLabelRelation.object_type) == cls.__name__
        ),
        backref='{0}_labels'.format(cls.__name__),
        cascade='all, delete-orphan')

  @sa.ext.hybrid.hybrid_property
  def labels(self):
    return self._labels

  @labels.setter
  def labels(self, values):
    """Setter function for labels.  """
    if values is None:
      return
    new_labels_set = {value['id'] for value in values}
    old_labels_dict = {label.id: label for label in self.labels}
    old_labels_set = set(old_labels_dict.keys())
    for id_to_remove in old_labels_set - new_labels_set:
      self._labels.remove(old_labels_dict[id_to_remove])
    for id_to_add in new_labels_set - old_labels_set:
      ObjectLabelRelation(object=self, label_id=id_to_add)

  @sa.orm.validates("labels")
  def validate_labels(self, _, value):
    """Validate assessment type to be the same as existing model name"""
    label_ids = {label.id for label in
                 Label.query.filter(Label.object_type == self.type)}
    for label_dict in value:
      if "id" not in label_dict:
        raise ValueError("Id field required to be the part of label dict")
      if int(label_dict["id"]) not in label_ids:
        raise ValueError(
            "Label with id {object_id} doesn't allowed to add "
            "to object type {object_type}".format(object_id=label_dict["id"],
                                                  object_type=self.type))
    return value

  @classmethod
  def eager_query(cls):
    return cls.eager_inclusions(
        super(Labeled, cls).eager_query(),
        Labeled._include_links
    ).options(
        sa.orm.subqueryload('labels')
    )

  @classmethod
  def indexed_query(cls):
    return super(
        Label,
        cls
    ).indexed_query(
    ).options(
        sa.orm.subqueryload(
            'labels'
        ).load_only(
            "name"
        )
    )

  def log_json(self):
    # pylint: disable=not-an-iterable
    res = super(Labeled, self).log_json()
    res["labels"] = [label.log_json() for label in self.labels]
    return res
