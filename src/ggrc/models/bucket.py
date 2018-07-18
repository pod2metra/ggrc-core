import uuid

import sqlalchemy
from sqlalchemy import func, orm, literal
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import functions
from ggrc import db
from ggrc.models.deferred import deferred
from ggrc.models.inflector import ModelInflectorDescriptor
from ggrc.models.mixins.base import Identifiable
from ggrc.models.reflection import AttributeInfo
from ggrc.utils import benchmark
from sqlalchemy_utils.types import UUIDType


def mapping_relation_factory(relation_name):

  __type_name = "{}_type".format(relation_name)
  __id_name = "{}_id".format(relation_name)
  __key_name = "{}_attr".format(relation_name)

  @property
  def key_maker(self):
    return "{}_{}".format(
        getattr(self, self.__type_name),
        relation_name)

  @property
  def value_getter(self):
    return getattr(self, getattr(self, __key_name), None)

  @value_getter.setter
  def value_setter(self, value):
    setattr(self, __type_name, getattr(value, 'type', None))
    setattr(self, __id_name, getattr(value, 'id', None))
    return setattr(self, getattr(self, __key_name), value)

  return type(
      "{}_mixin".format(relation_name),
      (object, ),
      {
          __type_name: db.Column(db.String, nullable=False),
          __id_name: db.Column(db.Integer, nullable=False),
          relation_name: value_getter,
          __key_name: key_maker,
      },
  )



class Bucket(Identifiable,
             mapping_relation_factory("key_obj"),
             mapping_relation_factory("scoped_obj"),
             db.Model):

    __tablename__ = "bucket_items"

    _inflector = ModelInflectorDescriptor()
    path = db.Column(db.String, nullable=False)
    parent_relationship_id = deferred(
        db.Column(
            db.Integer,
                db.ForeignKey(
                    'relationships.id',
                     ondelete='CASCADE',
                ),
            nullable=False,
        ),
        "Bucket",
    )
    parent_relationship = db.relationship(
        "Relationship",
        primaryjoin="Relationship.id == foreign(Bucket.parent_relationship_id)",
        uselist=False,
    )
    parent_bucket_id = db.Column(
        db.Integer,
        db.ForeignKey(
            'bucket_items.id',
            ondelete='CASCADE',
        ),
        nullable=True,
    )
    parent_bucket = db.relationship(
        lambda: Bucket,
        remote_side=lambda: Bucket.id
    )

    @staticmethod
    def _extra_table_args(klass):
      return (
          db.UniqueConstraint(
              'key_obj_id',
              'key_obj_type',
              'scoped_obj_id',
              'scoped_obj_type',
              'parent_relationship_id',
              'parent_bucket_id',
          ),
          db.Index(
              'ix_scoped_ob',
              'scoped_obj_type',
              'scoped_obj_id',
          ),
      )

    SCOPED_DICT = {
        u'AccessGroup': set([u'Comment', u'Document', u'Relationship']),
        u'Assessment': set([# u'Audit',
                            u'Comment',
                            u'Document',
                            u'Evidence',
                            u'Issue',
                            u'Relationship',
                            u'Snapshot']),
        u'Audit': set([u'Assessment',
                       u'AssessmentTemplate',
                       u'Comment',
                       u'Document',
                       u'Evidence',
                       u'Issue',
                       u'Relationship',
                       u'Snapshot']),
        u'Clause': set([u'Comment', u'Document', u'Relationship']),
        u'Comment': set([]),
        u'Contract': set([u'Comment', u'Document', u'Relationship']),
        u'Control': set([u'Comment', u'Document', u'Proposal', u'Relationship']),
        u'CycleTaskGroupObjectTask': set([]),
        u'DataAsset': set([u'Comment', u'Document', u'Relationship']),
        u'Document': set([u'Comment', u'Relationship']),
        u'Evidence': set([u'Comment', u'Relationship']),
        u'Facility': set([u'Comment', u'Document', u'Relationship']),
        u'Issue': set([u'Comment', u'Document', u'Relationship']),
        u'Market': set([u'Comment', u'Document', u'Relationship']),
        u'Metric': set([u'Comment', u'Document', u'Relationship']),
        u'Objective': set([u'Comment', u'Document', u'Relationship']),
        u'OrgGroup': set([u'Comment', u'Document', u'Relationship']),
        u'Policy': set([u'Comment', u'Document', u'Relationship']),
        u'Process': set([u'Comment', u'Document', u'Relationship']),
        u'Product': set([u'Comment', u'Document', u'Relationship']),
        u'ProductGroup': set([u'Comment', u'Document', u'Relationship']),
        u'Program': set([u'AccessGroup',
                         u'Assessment',
                         u'AssessmentTemplate',
                         u'Audit',
                         u'Clause',
                         u'Comment',
                         u'Contract',
                         u'Control',
                         u'DataAsset',
                         u'Document',
                         u'Evidence',
                         u'Facility',
                         u'Issue',
                         u'Market',
                         u'Metric',
                         u'Objective',
                         u'OrgGroup',
                         u'Policy',
                         u'Process',
                         u'Product',
                         u'ProductGroup',
                         u'Project',
                         u'Proposal',
                         u'Regulation',
                         u'Relationship',
                         u'Risk',
                         u'RiskAssessment',
                         u'Section',
                         u'Snapshot',
                         u'Standard',
                         u'System',
                         u'TechnologyEnvironment',
                         u'Threat',
                         u'Vendor']),
        u'Project': set([u'Comment', u'Document', u'Relationship']),
        u'Proposal': set([]),
        u'Regulation': set([u'Comment', u'Document', u'Relationship']),
        u'Risk': set([u'Comment', u'Document', u'Proposal', u'Relationship']),
        u'Section': set([u'Comment', u'Document', u'Relationship']),
        u'Snapshot': set([]),
        u'Standard': set([u'Comment', u'Document', u'Relationship']),
        u'System': set([u'Comment', u'Document', u'Relationship']),
        u'TaskGroupTask': set([]),
        u'TechnologyEnvironment': set([u'Comment', u'Document', u'Relationship']),
        u'Threat': set([u'Comment', u'Document', u'Relationship']),
        u'Vendor': set([u'Comment', u'Document', u'Relationship']),
        u'Workflow': set([])
     }

    @classmethod
    def scopes_generation(cls, relation):
      src_scope = cls.SCOPED_DICT.get(relation.source_type, [])
      dst_scope = cls.SCOPED_DICT.get(relation.destination_type, [])
      if relation.destination_type in src_scope:
        yield (relation.source_type,
               relation.source_id,
               relation.destination_type,
               relation.destination_id)
      if relation.source_type in dst_scope:
        yield (relation.destination_type,
               relation.destination_id,
               relation.source_type,
               relation.source_id)

    @classmethod
    def _propagate_scope_to_bucket(cls, bucket, scopes):
      for scope_type, scope_id, relation_id, path in scopes:
        db.session.add(cls(
          key_obj_type=bucket.key_obj_type,
          key_obj_id=bucket.key_obj_id,
          scoped_obj_type=scope_type,
          scoped_obj_id=scope_id,
          parent_relationship_id=relation_id,
          parent_bucket=bucket,
          path="{}->{}".format(bucket.key_obj_type, path)
        ))
    @classmethod
    def _propagate_bucket_step(cls,
                               relation,
                               key_obj_type,
                               key_obj_id,
                               scoped_obj_type,
                               scoped_obj_id):
      bucket = cls(
          key_obj_type=key_obj_type,
          key_obj_id=key_obj_id,
          scoped_obj_type=scoped_obj_type,
          scoped_obj_id=scoped_obj_id,
          parent_relationship=relation,
          path="{}->{}".format(key_obj_type, scoped_obj_type)
      )
      db.session.add(bucket)
      scopes = set(
          db.session.query(
              cls.scoped_obj_type.label("scoped_obj_type"),
              cls.scoped_obj_id.label("scoped_obj_id"),
              cls.parent_relationship_id.label("parent_relationship_id"),
              cls.path.label("path"),
          ).filter(
              cls.key_obj_type == scoped_obj_type,
              cls.key_obj_id == scoped_obj_id
          )
      )
      cls._propagate_scope_to_bucket(bucket, scopes)
      parent_buckets = set(cls.query.filter(
          cls.id.in_(
              db.session.query(
                  functions.coalesce(
                    cls.parent_bucket_id,
                    cls.id
                  )
              ).filter(
                  cls.scoped_obj_type == key_obj_type,
                  cls.scoped_obj_id == key_obj_id,
              )
          )
      ).options(
          orm.load_only("id", "key_obj_type", "key_obj_id", "path")
      ))
      for parent_bucket in parent_buckets:
          db.session.add(cls(
            key_obj_type=parent_bucket.key_obj_type,
            key_obj_id=parent_bucket.key_obj_id,
            scoped_obj_type=scoped_obj_type,
            scoped_obj_id=scoped_obj_id,
            parent_relationship=relation,
            parent_bucket=parent_bucket,
            path="{}->{}->{}".format(parent_bucket.key_obj_type,
                                     key_obj_type,
                                     scoped_obj_type)
          ))
          cls._propagate_scope_to_bucket(parent_bucket, scopes)

    @classmethod
    def propagate_bucket_via_relation(cls, relation):
      scopes = cls.scopes_generation(relation)
      for key_obj_type, key_obj_id, scoped_obj_type, scoped_obj_id in scopes:
        cls._propagate_bucket_step(relation,
                                   key_obj_type,
                                   key_obj_id,
                                   scoped_obj_type,
                                   scoped_obj_id)
