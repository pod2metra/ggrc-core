# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

from ggrc import db
from ggrc.builder import simple_property
from ggrc.models import reflection
from ggrc.models.mixins import Base
from ggrc.utils import create_stub


class ObjectFolder(Base, db.Model):
  __tablename__ = 'object_folders'

  folder_id = db.Column(db.String, nullable=False)
  parent_folder_id = db.Column(db.String, nullable=True)
  folderable_id = db.Column(db.Integer, nullable=False)
  folderable_type = db.Column(db.String, nullable=False)

  @property
  def folderable_attr(self):
    return '{0}_folderable'.format(self.folderable_type)

  @property
  def folderable(self):
    return getattr(self, self.folderable_attr)

  @folderable.setter
  def folderable(self, value):
    self.folderable_id = value.id if value is not None else None
    self.folderable_type = value.__class__.__name__ if value is not None \
        else None
    return setattr(self, self.folderable_attr, value)

  @staticmethod
  def _extra_table_args(cls):
    return (
        db.Index('ix_folderable_id_type', 'folderable_id', 'folderable_type'),
    )

  _api_attrs = reflection.ApiAttributes(
      'folder_id',
      'parent_folder_id',
      'folderable',
  )

  @classmethod
  def eager_query(cls):
    query = super(ObjectFolder, cls).eager_query()
    return query.options()

  def _display_name(self):
    return self.folderable.display_name + '<-> gdrive folder ' + self.folder_id


class Folderable(object):
  """Mixin adding the ability to attach folders to an object"""
  @classmethod
  def late_init_folderable(cls):
    def make_object_folders(cls):
      joinstr = 'and_(foreign(ObjectFolder.folderable_id) == {type}.id, '\
          'foreign(ObjectFolder.folderable_type) == "{type}")'
      joinstr = joinstr.format(type=cls.__name__)
      return db.relationship(
          'ObjectFolder',
          primaryjoin=joinstr,
          backref='{0}_folderable'.format(cls.__name__),
          cascade='all, delete-orphan',
      )

    cls.object_folders = make_object_folders(cls)

  @simple_property
  def folders(self):
    """Returns a list of associated folders' ids"""
    # pylint: disable=not-an-iterable
    return [{"id": fobject.folder_id} for fobject in self.object_folders]

  _api_attrs = reflection.ApiAttributes(
      'object_folders',
      reflection.Attribute('folders', create=False, update=False),
  )

  @classmethod
  def eager_query(cls):
    from sqlalchemy import orm

    query = super(Folderable, cls).eager_query()
    return query.options(
        orm.subqueryload('object_folders'))

  def log_json(self):
    """Serialize to JSON"""
    out_json = super(Folderable, self).log_json()
    if hasattr(self, "object_folders"):
      out_json["object_folders"] = [
          # pylint: disable=not-an-iterable
          create_stub(fold) for fold in self.object_folders if fold
      ]
    if hasattr(self, "folders"):
      out_json["folders"] = self.folders
    return out_json
