# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Full text index engine for Mysql DB backend"""

from sqlalchemy.ext.declarative import declared_attr

from ggrc import db


# pylint: disable=too-few-public-methods
class MysqlRecordProperty(db.Model):
  """ Db model for collect fulltext index records"""
  __tablename__ = 'fulltext_record_properties'

  ___slots___ = ("key", "type", "context_id", "tags", "property",
                 "subproperty", "content", "__tablename__", "__table_args__")

  key = db.Column(db.Integer, primary_key=True)
  type = db.Column(db.String(64), primary_key=True)
  context_id = db.Column(db.Integer)
  tags = db.Column(db.String)
  property = db.Column(db.String(250), primary_key=True)
  subproperty = db.Column(db.String(64), primary_key=True)
  content = db.Column(db.Text, nullable=False, default=u"")

  @declared_attr
  def __table_args__(cls):  # pylint: disable=no-self-argument
    return (
        db.Index('ix_{}_tags'.format(cls.__tablename__), 'tags'),
        db.Index('ix_{}_key'.format(cls.__tablename__), 'key'),
        db.Index('ix_{}_type'.format(cls.__tablename__), 'type'),
        db.Index('ix_{}_context_id'.format(cls.__tablename__), 'context_id'),
    )
