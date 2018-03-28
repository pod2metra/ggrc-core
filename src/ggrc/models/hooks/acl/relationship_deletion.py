# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""All hooks required by relationship unmapping"""

import sqlalchemy as sa
from sqlalchemy.sql.expression import and_

from ggrc import db
from ggrc.models import all_models


def delete_propagated(propagated_to, propagated_from):
    """Delete propagated roles if they were propagated by a relationship"""
    acl_table = all_models.AccessControlList.__table__
    parent_acl = all_models.AccessControlList.__table__.alias("parent_acl")
    ids = db.session.execute(
        sa.select([acl_table.c.id]).select_from(
            sa.join(acl_table, parent_acl,
                    acl_table.c.parent_id == parent_acl.c.id))
        .where(
            and_(
                acl_table.c.object_id == propagated_to.id,
                acl_table.c.object_type == propagated_to.type,
                parent_acl.c.object_id == propagated_from.id,
                parent_acl.c.object_type == propagated_from.type))).fetchall()
    if ids:
        db.session.execute(acl_table.delete().where(
            acl_table.c.id.in_(list(res[0] for res in ids))))


def after_flush(session):
    """Delete propagated relationships when the mapping is removed"""
    for obj in session.deleted:
        if not isinstance(obj, all_models.Relationship):
            continue
        delete_propagated(obj.source, obj.destination)
        delete_propagated(obj.destination, obj.source)
