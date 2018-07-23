# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Access Control List model"""
import itertools
from collections import defaultdict

import flask
import sqlalchemy as sa
from sqlalchemy import distinct, literal
from sqlalchemy.orm import aliased

from ggrc import db
from ggrc.access_control.role import PropagatedAccessControlRole
from ggrc.builder import simple_property
from ggrc.models import mixins
from ggrc.models import reflection
from ggrc.models.deferred import deferred
from ggrc.models.mixins import base
from ggrc.access_control import mixins as acl_mixins
from ggrc.utils import list_chunks


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

  @staticmethod
  def get_pacr_objs():
    if hasattr(flask.g, "pacr_obj_dict"):
      return flask.g.pacr_obj_dict
    flask.g.pacr_obj_dict = defaultdict(set)
    query = PropagatedAccessControlRole.query.all()
    for pacr in query:
      flask.g.pacr_obj_dict[pacr.parent_id].add(pacr)
    return flask.g.pacr_obj_dict

  def propagated_acl_generator(self, relationship_ids):
    pacrs = self.get_pacr_objs()[self.ac_role_id]
    from ggrc.models.all_models import Bucket
    if relationship_ids:
      rel_statement = Bucket.parent_relationship_id.in_(relationship_ids)
    else:
      rel_statement = True
    for pacr in pacrs:
      if self.ac_role_id is None:
        continue
      if '<-' in pacr.nodes[0]:
        # reversed propagation
        r_nodes = pacr.nodes[0].split("<-")[::-1]
        reversed_path = "->".join(r_nodes)
        r_buckets = db.session.query(
            Bucket.id.label("b_id"),
            Bucket.left_obj_type.label("obj_type"),
            Bucket.left_obj_id.label("obj_id"),
            literal(pacr.id).label("pacr_id"),
            literal(pacr.read).label("read"),
            literal(pacr.update).label("update"),
            literal(pacr.delete).label("delete"),
            literal(self.person_id).label("person_id"),
            literal(self.id).label("parent_id"),
        ).filter(
            Bucket.path == reversed_path,
            Bucket.right_obj_type == self.object_type,
            Bucket.right_obj_id == self.object_id,
            rel_statement,
        )
        if len(pacr.nodes) == 1:
          yield r_buckets
        else:
          r_buckets = r_buckets.subquery()
          yield db.session.query(
              Bucket.id,
              Bucket.right_obj_type,
              Bucket.right_obj_id,
              literal(pacr.id).label("pacr_id"),
              literal(pacr.read).label("read"),
              literal(pacr.update).label("update"),
              literal(pacr.delete).label("delete"),
              literal(self.person_id).label("person_id"),
              literal(self.id).label("parent_id"),
          ).filter(
              Bucket.left_obj_id == r_buckets.c.obj_id,
              Bucket.left_obj_type == r_buckets.c.obj_type,
              Bucket.path == "->".join([r_nodes[0]] + pacr.nodes[1:]),
              rel_statement,
          )
      else:
        yield db.session.query(
            Bucket.id,
            Bucket.right_obj_type,
            Bucket.right_obj_id,
            literal(pacr.id).label("pacr_id"),
            literal(pacr.read).label("read"),
            literal(pacr.update).label("update"),
            literal(pacr.delete).label("delete"),
            literal(self.person_id).label("person_id"),
            literal(self.id).label("parent_id"),
        ).filter(
            Bucket.left_obj_id == self.object_id,
            Bucket.left_obj_type == self.object_type,
            Bucket.path == pacr.for_path,
            rel_statement,
        )

  def propagate(self):
    queries = [i for i in self.propagated_acl_generator(None)
               if i is not None]
    if not queries:
      return
    db.session.execute(
      self.__table__.insert().from_select(
        [
          "parent_bucket_id",
          "object_type",
          "object_id",
          "p_ac_role_id",
          "read",
          "update",
          "delete",
          "person_id",
          "parent_id"
        ],
        sa.union_all(*queries)
      )
    )


  @classmethod
  def propagate_ids(cls, *acl_ids, **kwargs):
    if not acl_ids:
      return
    from ggrc.models import all_models
    simple_propagation = db.session.query(
        all_models.Bucket.id,
        all_models.Bucket.right_obj_type,
        all_models.Bucket.right_obj_id,
        all_models.PropagatedAccessControlRole.id.label("pacr_id"),
        all_models.PropagatedAccessControlRole.read,
        all_models.PropagatedAccessControlRole.update,
        all_models.PropagatedAccessControlRole.delete,
        cls.person_id.label("person_id"),
        cls.id.label("parent_id"),
    ).select_from(
        cls
    ).join(
        all_models.AccessControlRole,
        all_models.AccessControlRole.id == cls.ac_role_id
    ).join(
        all_models.PropagatedAccessControlRole,
        all_models.PropagatedAccessControlRole.parent_id == all_models.AccessControlRole.id
    ).join(
        all_models.Bucket,
        sa.and_(
            all_models.Bucket.path == all_models.PropagatedAccessControlRole.for_down_path,
            all_models.PropagatedAccessControlRole.for_up_path == "",
            all_models.Bucket.left_obj_type == cls.object_type,
            all_models.Bucket.left_obj_id == cls.object_id
        )
    ).filter(
        cls.id.in_(acl_ids)
    )
    parent_propagation = db.session.query(
        all_models.Bucket.id,
        all_models.Bucket.left_obj_type,
        all_models.Bucket.left_obj_id,
        all_models.PropagatedAccessControlRole.id.label("pacr_id"),
        all_models.PropagatedAccessControlRole.read,
        all_models.PropagatedAccessControlRole.update,
        all_models.PropagatedAccessControlRole.delete,
        cls.person_id.label("person_id"),
        cls.id.label("parent_id"),
    ).select_from(
        cls
    ).join(
        all_models.AccessControlRole,
        all_models.AccessControlRole.id == cls.ac_role_id
    ).join(
        all_models.PropagatedAccessControlRole,
        all_models.PropagatedAccessControlRole.parent_id == all_models.AccessControlRole.id
    ).join(
        all_models.Bucket,
        sa.and_(
            all_models.Bucket.path == all_models.PropagatedAccessControlRole.for_up_path,
            all_models.PropagatedAccessControlRole.for_down_path == "",
            all_models.Bucket.right_obj_type == cls.object_type,
            all_models.Bucket.right_obj_id == cls.object_id
        )
    ).filter(
        cls.id.in_(acl_ids)
    )
    pb = aliased(all_models.Bucket)
    parant_scope_propagation = db.session.query(
        all_models.Bucket.id,
        all_models.Bucket.right_obj_type,
        all_models.Bucket.right_obj_id,
        all_models.PropagatedAccessControlRole.id.label("pacr_id"),
        all_models.PropagatedAccessControlRole.read,
        all_models.PropagatedAccessControlRole.update,
        all_models.PropagatedAccessControlRole.delete,
        cls.person_id.label("person_id"),
        cls.id.label("parent_id"),
  ).select_from(
        cls
    ).join(
        all_models.AccessControlRole,
        all_models.AccessControlRole.id == cls.ac_role_id
    ).join(
        all_models.PropagatedAccessControlRole,
        all_models.PropagatedAccessControlRole.parent_id == all_models.AccessControlRole.id
    ).join(
        pb,
        sa.and_(
            pb.path == all_models.PropagatedAccessControlRole.for_up_path,
            all_models.PropagatedAccessControlRole.for_down_path != "",
            pb.right_obj_type == cls.object_type,
            pb.right_obj_id == cls.object_id
        )
    ).join(
        all_models.Bucket,
        sa.and_(
            all_models.Bucket.path == all_models.PropagatedAccessControlRole.for_down_path,
            all_models.Bucket.left_obj_type == pb.right_obj_type,
            all_models.Bucket.left_obj_id == pb.right_obj_id
        )
    ).filter(
        cls.id.in_(acl_ids)
    )
    db.session.execute(
        cls.__table__.insert().from_select(
            [
                "parent_bucket_id",
                "object_type",
                "object_id",
                "p_ac_role_id",
                "read",
                "update",
                "delete",
                "person_id",
                "parent_id"
            ],
            sa.union_all(
                simple_propagation,
                parent_propagation,
                parant_scope_propagation,
            )
        )
    )

  @classmethod
  def propagate_via_relationships(cls, relationship):
    propagatable_query = cls.query.filter(cls.ac_role_id.isnot_(None))
    acls = propagatable_query.filter(
        cls.object_type == relationship.source_type,
        cls.object_id == relationship.source_id,
    ).union(
        cls.object_type == relationship.destination_type,
        cls.object_id == relationship.destination_id,
    )
    for acl in acls:
      acl.propagate(relationship.id)
