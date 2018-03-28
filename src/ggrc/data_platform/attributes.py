# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Attributes module."""

from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr

from ggrc import db
from ggrc.data_platform import base


class Attributes(base.Base, db.Model):
    """Attributes model."""
    __tablename__ = 'attributes'

    attribute_id = db.Column(db.Integer, primary_key=True)
    # object id should eventually be a foreign key to objects table
    object_id = db.Column(db.Integer)
    object_type = db.Column(db.Unicode(250))
    attribute_definition_id = db.Column(
        db.Integer,
        db.ForeignKey('attribute_definitions.attribute_definition_id'))
    attribute_template_id = db.Column(
        db.Integer, db.ForeignKey('attribute_templates.attribute_template_id'))

    # value string is not nullable to avoid weird filtering behavior. This is
    # different than on data platform, but needed here because we decided to make
    # all text fields mandatory with default empty string
    value_string = db.Column(db.UnicodeText, nullable=False, default=u"")
    value_integer = db.Column(db.Integer)
    value_datetime = db.Column(db.DateTime)

    # ggrc specific code, needs to be added back to DP.
    source_type = db.Column(db.Unicode(250))
    source_id = db.Column(db.Integer)
    source_attr = db.Column(db.Unicode(250))

    namespace_id = db.Column(
        db.Integer, db.ForeignKey('namespaces.namespace_id'), nullable=True)

    deleted = db.Column(db.Boolean, default=False)
    version = db.Column(db.Integer)

    attribute_definition = orm.relationship(
        "AttributeDefinitions", backref="attributes")
    attribute_template = orm.relationship(
        "AttributeTemplates", backref="attributes")

    namespace = orm.relationship("Namespaces", backref="attributes")

    @declared_attr
    def __table_args__(cls):  # pylint: disable=no-self-argument
        return (
            db.Index("ix_source", "source_type", "source_id", "source_attr"),
            # db.Index("value_string"), not needed yet
            db.Index("ix_value_integer", "value_integer"),
            db.Index("ix_value_datetime", "value_datetime"),
            db.UniqueConstraint(
                "object_id",
                "object_type",
                "attribute_definition_id",
                "attribute_template_id",
                name="uq_attributes",
            ),
        )
