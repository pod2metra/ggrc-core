# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
""" Model for labels association table."""

from sqlalchemy import orm
from sqlalchemy.orm import validates

from ggrc import db
from ggrc.models import mixins
from ggrc.models import reflection
from ggrc.fulltext.mixin import Indexed


class Label(mixins.Base, db.Model, Indexed):
    """Represent object labels"""
    __tablename__ = 'labels'
    _fulltext_attrs = [
        'name',
        'object_type',
    ]

    @validates('name')
    def validate_name(self, key, value):
        """Validates and cleans name that has leading/trailing spaces"""
        # pylint: disable=unused-argument,no-self-use
        return value if value is None else value.strip()

    name = db.Column(db.String, nullable=False)
    object_type = db.Column(db.String)

    _api_attrs = reflection.ApiAttributes("name")

    _extra_table_args = [
        db.UniqueConstraint('name', 'object_type'),
    ]

    @classmethod
    def indexed_query(cls):
        return super(Label, cls).indexed_query().options(
            orm.Load(cls).load_only("name", "object_type"), )
