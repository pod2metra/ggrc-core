# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Resolve duplicates.

This helper is used by the following migrations:

* ggrc.migrations.verisions.20160223152916_204540106539;
* ggrc_risk_assessments.migrations.verisions.20151112161029_62f26762d0a.

"""

from collections import defaultdict

from alembic import op

import sqlalchemy as sa
from sqlalchemy import and_
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import aliased
from sqlalchemy.sql import table

from ggrc import db
from ggrc.models import CustomAttributeDefinition


def resolve_duplicates(model, attr, separator=u"-"):
    """Resolve duplicates on a model property

  Check and remove by renaming duplicate attribute for values.

  Args:
    model: model that will be checked
    attr: attribute that will be checked
    separator: (default -) Separator between old attr value and integer
  """
    # pylint: disable=invalid-name
    v0, v1 = aliased(model, name="v0"), aliased(model, name="v1")
    query = db.session.query(v0).join(v1,
                                      and_(
                                          getattr(v0, attr) == getattr(
                                              v1, attr), v0.id > v1.id))
    for v in query:
        i = 1
        nattr = "{}{}{}".format(getattr(v, attr, model.type), separator, i)
        while db.session.query(model).\
                filter(getattr(model, attr) == nattr).count():
            i += 1
            nattr = "{}{}{}".format(getattr(v, attr, model.type), separator, i)
        setattr(v, attr, nattr)
        db.session.add(v)
        db.session.flush()
    db.session.commit()


def create_new_table(name, *columns):
    """Create table and return SQLAlchemy table object"""
    # Ignore error if table already exists
    try:
        op.create_table(name, *columns)
    except OperationalError:
        pass
    return table(name, *columns)


def rename_ca_title(renaming_title, definition_types):
    """Rename Custom Attributes title to 'old_title-{number}'

  Args:
    renaming_title(str): Title that should be renamed
    definition_types(list): Definition types of CA that should be renamed
  """
    cads = db.session.query(
        CustomAttributeDefinition.id,
        CustomAttributeDefinition.definition_type,
        CustomAttributeDefinition.title,
    ).filter(
        CustomAttributeDefinition.title.contains(renaming_title),
        CustomAttributeDefinition.definition_type.in_(definition_types))

    # Collect titles containing renaming_title
    existing_ca_titles = defaultdict(set)
    conflicting_ca = {}
    for id_, def_type, title in cads:
        existing_ca_titles[def_type].add(title.lower())
        if title.lower() == renaming_title.lower():
            conflicting_ca[id_] = def_type

    # Collect CA ids and new titles for update
    new_ca_titles = []
    for ca_id, ca_type in conflicting_ca.items():
        attempt = 1
        while True:
            new_ca_name = "{}-{}".format(renaming_title, attempt)
            if new_ca_name.lower() in existing_ca_titles[ca_type]:
                attempt += 1
            else:
                new_ca_titles.append({"id": ca_id, "title": new_ca_name})
                break

    temp_tbl = create_new_table("new_ca_titles", sa.Column("id", sa.Integer),
                                sa.Column("title", sa.String(length=250)))
    # Update CADs with temporary table
    op.bulk_insert(temp_tbl, new_ca_titles)
    op.execute("""
      update custom_attribute_definitions
      join new_ca_titles
        on custom_attribute_definitions.id = new_ca_titles.id
      set custom_attribute_definitions.title = new_ca_titles.title
  """)
    op.drop_table("new_ca_titles")
