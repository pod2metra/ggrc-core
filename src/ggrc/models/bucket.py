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


BUCKETING_RULLES = {
    "Program": ["Audit",
                "Assessment",
                "Control",
                "Risk",
                "Issue",
                "Comment",
                "Document",
                "Evidence",
                "AssessmentTemplate",

                ]


}


class Bucket(Identifiable,
             mapping_relation_factory("key_obj"),
             mapping_relation_factory("scoped_obj"),
             db.Model):

    __tablename__ = "bucket_items"

    _inflector = ModelInflectorDescriptor()

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
        "TechnologyEnvironment": ["Comment", "Document"],
        "OrgGroup": ["Comment", "Document"],
        "Section": ["Document", "Comment"],
        "AccessGroup": ["Comment", "Document"],
        "System": ["Comment", "Document"],
        "ProductGroup": ["Comment", "Document"],
        "Objective": ["Document", "Comment"],
        "Regulation": ["Document", "Comment"],
        "Program": ["AssessmentTemplate",
                    "Assessment",
                    "Comment",
                    "Document",
                    "OrgGroup",
                    "Proposal",
                    "AccessGroup",
                    "Audit",
                    "Clause",
                    "Comment",
                    "Contract",
                    "Control",
                    "DataAsset",
                    "Document",
                    "Evidence" ,
                    "Facility",
                    "Issue",
                    "Issue",
                    "Market",
                    "Metric",
                    "Objective",
                    "Process",
                    "Product",
                    "ProductGroup",
                    "Project",
                    "Regulation",
                    "Risk",
                    "RiskAssessment",
                    "Section",
                    "Snapshot",
                    "Standard",
                    "System",
                    "TechnologyEnvironment",
                    "Threat",
                    "Vendor"],

      "Policy": ["Comment", "Document"],
      "Document": ["Comment"],
      "Issue": ["Document", "Comment"],
      "Product": ["Comment", "Document"],
      "Vendor": ["Comment", "Document"],
      "Risk": ["Comment",
               "Document",
               "Proposal"],
      "Workflow": [],
      "CycleTaskGroupObjectTask": [],
      "Assessment": ["Issue",
                     "Document",
                     "Comment",
                     "Snapshot",
                     "Evidence"],
      "Standard": ["Comment", "Document"],
      "Audit": ["Assessment",
                "AssessmentTemplate",
                "Comment",
                "Evidence",
                "Issue",
                "Snapshot",
                "Comment",
                "Document"],
      "Control": ["Document", "Comment", "Proposal"],
      "Contract": ["Document", "Comment"],
      "Project": ["Comment", "Document"],
      "DataAsset": ["Comment", "Document"],
      "Threat": ["Comment", "Document"],
      "TaskGroupTask": [],
      "Comment": [],
      "Facility": ["Document", "Comment"],
      "Process": ["Comment", "Document"],
      "Clause": ["Comment", "Document"],
      "Metric": ["Document", "Comment"],
      "Evidence": ["Comment"],
      "Market": ["Document", "Comment"],
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
      for scope_type, scope_id, relation_id in scopes:
        db.session.add(cls(
          key_obj_type=bucket.key_obj_type,
          key_obj_id=bucket.key_obj_id,
          scoped_obj_type=scope_type,
          scoped_obj_id=scope_id,
          parent_relationship_id=relation_id,
          parent_bucket=bucket,
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
      )
      db.session.add(bucket)
      scopes = set(
          db.session.query(
              cls.scoped_obj_type.label("scoped_obj_type"),
              cls.scoped_obj_id.label("scoped_obj_id"),
              cls.parent_relationship_id.label("parent_relationship_id"),
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
          orm.load_only("id", "key_obj_type", "key_obj_id")
      ))
      for parent_bucket in parent_buckets:
          db.session.add(cls(
            key_obj_type=parent_bucket.key_obj_type,
            key_obj_id=parent_bucket.key_obj_id,
            scoped_obj_type=scoped_obj_type,
            scoped_obj_id=scoped_obj_id,
            parent_relationship=relation,
            parent_bucket=parent_bucket,
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
