# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Access Control List model"""

import sqlalchemy as sa

from ggrc import db
from ggrc.access_control.role import PropagatedAccessControlRole
from ggrc.builder import simple_property
from ggrc.models import mixins
from ggrc.models import reflection
from ggrc.models.deferred import deferred
from ggrc.models.mixins import base
from ggrc.access_control import mixins as acl_mixins


class AccessControlList(base.ContextRBAC,
                        acl_mixins.PermissionMixin,
                        mixins.Base,
                        db.Model):
  """Access Control List

  Model is a mapping between a role a person and an object. It gives the
  permission of the role to the person from that object.
  """
  __tablename__ = 'access_control_list'
  _api_attrs = reflection.ApiAttributes(
      "person",
      reflection.Attribute("person_id", create=False, update=False),
      reflection.Attribute("person_email", create=False, update=False),
      reflection.Attribute("person_name", create=False, update=False),
      "ac_role_id"
  )

  person_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
  ac_role_id = db.Column(
      db.Integer,
      db.ForeignKey('access_control_roles.id'),
      nullable=True)
  p_ac_role_id = db.Column(
      db.Integer,
      db.ForeignKey('propagated_access_control_roles.id'),
      nullable=True)
  object_id = db.Column(db.Integer, nullable=False)
  object_type = db.Column(db.String, nullable=False)

  parent_id_nn = db.Column(
      db.Integer,
      nullable=False,
      default="0",
  )
  parent_id = db.Column(
      db.Integer,
      db.ForeignKey('access_control_list.id', ondelete='CASCADE'),
      nullable=True,
  )
  parent = db.relationship(
      lambda: AccessControlList,  # pylint: disable=undefined-variable
      remote_side=lambda: AccessControlList.id
  )
  parent_bucket_id = db.Column(
      db.Integer,
      db.ForeignKey(
          'bucket_items.id',
          ondelete='CASCADE',
      ),
      nullable=True,
  )


  @simple_property
  def person_email(self):
    return self.person.email if self.person else None

  @simple_property
  def person_name(self):
    return self.person.name if self.person else None

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
        db.UniqueConstraint(
            'person_id',
            'ac_role_id',
            'object_id',
            'object_type',
            'parent_id_nn',
        ),
        db.Index('idx_object_type_object_idx', 'object_type', 'object_id'),
        db.Index('ix_person_object', 'person_id', 'object_type', 'object_id'),
        db.Index(
            'idx_object_type_object_id_parent_id_nn',
            'object_type',
            'object_id',
            'parent_id_nn',
        ),
    )
