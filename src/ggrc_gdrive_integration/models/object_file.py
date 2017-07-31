# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

from sqlalchemy import orm

from ggrc import db
from ggrc.models.mixins import Base
from ggrc.utils import create_stub
from ggrc.models import reflection


class ObjectFile(Base, db.Model):
  __tablename__ = 'object_files'

  file_id = db.Column(db.String, nullable=False)
  parent_folder_id = db.Column(db.String, nullable=True)
  fileable_id = db.Column(db.Integer, nullable=False)
  fileable_type = db.Column(db.String, nullable=False)

  @property
  def fileable_attr(self):
    return '{0}_fileable'.format(self.fileable_type)

  @property
  def fileable(self):
    return getattr(self, self.fileable_attr)

  @fileable.setter
  def fileable(self, value):
    self.fileable_id = value.id if value is not None else None
    self.fileable_type = value.__class__.__name__ if value is not None \
        else None
    return setattr(self, self.fileable_attr, value)

  _api_attrs = reflection.ApiAttributes(
      'file_id',
      'parent_folder_id',
      'fileable',
  )

  @classmethod
  def eager_query(cls):
    query = super(ObjectFile, cls).eager_query()
    return query.options()

  def _display_name(self):
    return self.fileable.display_name + '<-> gdrive file' + self.file_id


class Fileable(object):

  @classmethod
  def late_init_fileable(cls):
    def make_object_files(cls):
      joinstr = 'and_(foreign(ObjectFile.fileable_id) == {type}.id, '\
          'foreign(ObjectFile.fileable_type) == "{type}")'
      joinstr = joinstr.format(type=cls.__name__)
      return db.relationship(
          'ObjectFile',
          primaryjoin=joinstr,
          backref='{0}_fileable'.format(cls.__name__),
          cascade='all, delete-orphan',
      )

    cls.object_files = make_object_files(cls)

  _api_attrs = reflection.ApiAttributes('object_files', )

  @classmethod
  def eager_query(cls):
    query = super(Fileable, cls).eager_query()
    return query.options(
        orm.subqueryload('object_files'))

  def log_json(self):
    """Serialize to JSON"""
    out_json = super(Fileable, self).log_json()
    if hasattr(self, "object_files"):
      out_json["object_files"] = [
          # pylint: disable=not-an-iterable
          create_stub(file) for file in self.object_files if file
      ]
    return out_json
