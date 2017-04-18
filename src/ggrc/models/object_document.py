# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

from sqlalchemy import orm, case
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr

from ggrc import db
from ggrc.models import reflection
from ggrc.models.deferred import deferred
from ggrc.models.document import Document
from ggrc.models.mixins import Base
from ggrc.models.mixins import Timeboxed
from ggrc.models.relationship import Relationship
from ggrc.utils import create_stub


class ObjectDocument(Timeboxed, Base, db.Model):
  __tablename__ = 'object_documents'

  role = deferred(db.Column(db.String), 'ObjectDocument')
  notes = deferred(db.Column(db.Text), 'ObjectDocument')
  document_id = db.Column(db.Integer, db.ForeignKey('documents.id'),
                          nullable=False)
  documentable_id = db.Column(db.Integer, nullable=False)
  documentable_type = db.Column(db.String, nullable=False)

  @property
  def documentable_attr(self):
    return '{0}_documentable'.format(self.documentable_type)

  @property
  def documentable(self):
    return getattr(self, self.documentable_attr)

  @documentable.setter
  def documentable(self, value):
    self.documentable_id = value.id if value is not None else None
    self.documentable_type = value.__class__.__name__ if value is not None \
        else None
    return setattr(self, self.documentable_attr, value)

  # properties to integrate into revision indexing
  @property
  def source_type(self):
    return "Document"

  @property
  def source_id(self):
    return self.document_id

  @property
  def destination_type(self):
    return self.documentable_type

  @property
  def destination_id(self):
    return self.documentable_id

  @staticmethod
  def _extra_table_args(cls):
    return (
        db.UniqueConstraint('document_id',
                            'documentable_id',
                            'documentable_type'),
        db.Index('ix_document_id', 'document_id'),
    )

  _publish_attrs = [
      'role',
      'notes',
      'document',
      'documentable',
  ]
  _sanitize_html = [
      'notes',
  ]

  @classmethod
  def eager_query(cls):
    query = super(ObjectDocument, cls).eager_query()
    return query.options(
        orm.subqueryload('document'))

  def _display_name(self):
    return self.documentable.display_name + '<->' + self.document.display_name


class Documentable(object):
  """Base class for EvidenceURL mixin"""
  @declared_attr
  def object_documents(cls):
    """Returns all the associated documents"""
    cls.documents = association_proxy(
        'object_documents', 'document',
        creator=lambda document: ObjectDocument(
            document=document,
            documentable_type=cls.__name__,
        )
    )
    joinstr = ('and_(foreign(ObjectDocument.documentable_id) == {type}.id, '
               '     foreign(ObjectDocument.documentable_type) == "{type}")')
    joinstr = joinstr.format(type=cls.__name__)
    return db.relationship(
        'ObjectDocument',
        primaryjoin=joinstr,
        backref='{0}_documentable'.format(cls.__name__),
        cascade='all, delete-orphan',
    )

  _publish_attrs = [
      reflection.PublishOnly('documents'),
      'object_documents',
  ]

  _include_links = [
      # 'object_documents',
  ]

  @classmethod
  def eager_query(cls):
    query = super(Documentable, cls).eager_query()
    return cls.eager_inclusions(query, Documentable._include_links).options(
        orm.subqueryload('object_documents'))

  def log_json(self):
    """Serialize to JSON"""
    out_json = super(Documentable, self).log_json()
    if hasattr(self, "documents"):
      out_json["documents"] = [
          # pylint: disable=not-an-iterable
          create_stub(doc) for doc in self.documents if doc
      ]
    if hasattr(self, "object_documents"):
      out_json["object_documents"] = [
          # pylint: disable=not-an-iterable
          create_stub(doc) for doc in self.object_documents if doc
      ]
    return out_json

  @classmethod
  def indexed_query(cls):
    query = super(Documentable, cls).indexed_query()
    return query.options(
        orm.subqueryload(
            "object_documents"
        ).load_only(
            "id",
            "documentable_id",
            "documentable_type",
        )
    )


class EvidenceURL(Documentable):
  """Documentable mixin for evidence and URL documents."""

  _aliases = {
      "document_url": {
          "display_name": "Url",
          "type": reflection.AttributeInfo.Type.SPECIAL_MAPPING,
          "description": "New line separated list of URLs.",
      },
      "document_evidence": {
          "display_name": "Evidence",
          "type": reflection.AttributeInfo.Type.SPECIAL_MAPPING,
          "description": ("New line separated list of evidence links and "
                          "titles.\nExample:\n\nhttp://my.gdrive.link/file "
                          "Title of the evidence link"),
      },
  }

  @declared_attr
  def _assessment_documents(self):
    """ """
    document_id = case(
        [(
            Relationship.destination_type == "Document",
            Relationship.destination_id,
        )],
        else_=Relationship.source_id
    )
    documentable_id = case(
        [(Relationship.destination_type == "Document",
          Relationship.source_id)],
        else_=Relationship.destination_id,
    )

    return db.relationship(
        Document,
        primaryjoin=lambda: self.id == documentable_id,
        secondary=Relationship.__table__,
        secondaryjoin=lambda: Document.id == document_id,
        viewonly=True,
    )

  @property
  def assessment_documents(self):
    return self._assessment_documents

  def documents_by_type(self, doc_type):
    """Returns a list of document objects of requested type"""
    if doc_type == "document_evidence":
      # pylint: disable=not-an-iterable
      return [instance.document for instance in self.object_documents]
    if doc_type == "document_url":
      return self.assessment_documents

  @classmethod
  def indexed_query(cls):
    query = super(EvidenceURL, cls).indexed_query()
    return query.options(
        orm.subqueryload(
            "_assessment_documents"
        ).load_only(
            "id",
            "title",
            "link"
        )
    )
