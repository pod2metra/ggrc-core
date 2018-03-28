# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Contains WithSimilarityScore mixin.

This defines a procedure of getting "similar" objects which have similar
relationships.
"""

import sqlalchemy as sa

from ggrc import db
from ggrc.models.relationship import Relationship
from ggrc.models.snapshot import Snapshot

DEFAULT_WEIGHT = 1


class WithSimilarityScore(object):
    """Defines a routine to get similar object with mappings to same objects."""

    # pylint: disable=too-few-public-methods
    @classmethod
    def get_similar_objects_query(cls, id_, type_):
        """Get objects of types similar to cls instance by their mappings.

    Args:
        id_: the id of the object to which the search will be applied.
        type_: type of similar object.

    Returns:
        SQLAlchemy query that yields results with columns [(id,)] -
        the id of similar objects.
    """
        from ggrc.snapshotter.rules import Types
        if cls.__name__ in Types.all and type_ in Types.scoped:
            return cls._similar_obj_assessment(type_, id_)
        elif cls.__name__ in Types.scoped and type_ in Types.scoped:
            return cls._similar_asmnt_assessment(type_, id_)
        elif cls.__name__ in Types.scoped and type_ in Types.trans_scope:
            return cls._similar_asmnt_issue(type_, id_)
        return []

    @classmethod
    def _similar_obj_assessment(cls, type_, id_):
        """Find similar Assessments for object.

    Args:
        type_: Object type.
        id_: Object id.

    Returns:
        SQLAlchemy query that yields results [(similar_id,)] - the id of
        similar objects.
    """
        from ggrc.models import all_models
        # Find objects directly mapped to Snapshot of base object
        # Object1 <-> Snapshot of Object1 <-> Object2
        similar_queries = cls.mapped_to_obj_snapshot(cls.__name__, id_)

        # Find objects mapped to Snapshot of base object through another object
        # Object1 <-> Object2 <-> Snapshot of Object2 <-> Object3
        mapped_obj = cls.mapped_objs(cls.__name__, id_, True)
        similar_queries += cls.mapped_to_obj_snapshot(mapped_obj.c.obj_type,
                                                      mapped_obj.c.obj_id)
        similar_objs = sa.union_all(*similar_queries).alias("similar_objs")
        return db.session.query(similar_objs.c.similar_id).join(
            all_models.Assessment,
            sa.and_(
                all_models.Assessment.assessment_type == cls.__name__,
                all_models.Assessment.id == similar_objs.c.similar_id,
            )).filter(similar_objs.c.similar_type == type_, )

    @classmethod
    def _similar_asmnt_assessment(cls, type_, id_):
        """Find similar Assessments for Assessment object.

    Args:
        type_: Assessment type.
        id_: Assessment id.

    Returns:
        SQLAlchemy query that yields results [(similar_id,)] - the id of
        similar objects.
    """
        from ggrc.models import all_models
        asmnt = all_models.Assessment

        asmnt_mapped = cls.mapped_to_assessment([id_]).subquery()
        # Find Assessments directly mapped to Snapshot of same object
        similar_queries = cls.mapped_to_obj_snapshot(asmnt_mapped.c.obj_type,
                                                     asmnt_mapped.c.obj_id)

        # Find Assessments mapped to Snapshot of object mapped to base object
        # Object1 <-> Object2 <-> Snapshot of Object2 <-> Assessment
        mapped_obj = cls.mapped_objs(asmnt_mapped.c.obj_type,
                                     asmnt_mapped.c.obj_id, True)
        similar_queries += cls.mapped_to_obj_snapshot(mapped_obj.c.obj_type,
                                                      mapped_obj.c.obj_id)

        similar_objs = sa.union_all(*similar_queries).alias("scoped_similar")
        return db.session.query(similar_objs.c.similar_id).join(
            asmnt,
            sa.and_(
                asmnt.assessment_type == similar_objs.c.related_type,
                asmnt.id == similar_objs.c.similar_id,
            )).filter(
                asmnt.id != id_,
                similar_objs.c.similar_type == type_,
            )

    @classmethod
    def _similar_asmnt_issue(cls, type_, id_):
        """Find similar Issues for Assessment.

    Args:
        type_: Assessment type.
        id_: Assessment id.

    Returns:
        SQLAlchemy query that yields results [(similar_id,)] - the id of
        similar objects.
    """
        mapped_obj = cls.mapped_to_assessment([id_]).subquery()
        similar_queries = cls.mapped_to_obj_snapshot(mapped_obj.c.obj_type,
                                                     mapped_obj.c.obj_id)
        mapped_related = cls.mapped_objs(mapped_obj.c.obj_type,
                                         mapped_obj.c.obj_id)
        similar_queries.append(
            db.session.query(
                mapped_related.c.obj_id.label("similar_id"),
                mapped_related.c.obj_type.label("similar_type"),
                mapped_related.c.base_type.label("related_type"),
            ))
        similar_objs = sa.union_all(*similar_queries).alias("scoped_similar")
        return db.session.query(similar_objs.c.similar_id).filter(
            similar_objs.c.similar_type == type_, )

    @classmethod
    def mapped_to_assessment(cls, related_ids):
        """Collect objects that have snapshot mapped to assessment.

    Args:
        related_ids: List of Assessment ids.

    Returns:
        SQLAlchemy query with id and type of found
        objects [(obj_id, obj_type)].
    """
        from ggrc.models import all_models
        asmnt = all_models.Assessment

        objects_mapped = sa.union_all(
            db.session.query(
                Snapshot.child_id.label("obj_id"),
                asmnt.assessment_type.label("obj_type"),
            ).join(Relationship,
                   sa.and_(
                       Relationship.source_id == Snapshot.id,
                       Relationship.source_type == Snapshot.__name__,
                   )).join(asmnt,
                           sa.and_(
                               Relationship.destination_type == asmnt.__name__,
                               Relationship.destination_id == asmnt.id,
                           )).filter(
                               asmnt.id.in_(related_ids),
                               Snapshot.child_type == asmnt.assessment_type,
                           ),
            db.session.query(
                Snapshot.child_id.label("obj_id"),
                asmnt.assessment_type.label("obj_type"),
            ).join(Relationship,
                   sa.and_(
                       Relationship.destination_id == Snapshot.id,
                       Relationship.destination_type == Snapshot.__name__,
                   )).join(asmnt,
                           sa.and_(
                               Relationship.source_type == asmnt.__name__,
                               Relationship.source_id == asmnt.id,
                           )).filter(
                               asmnt.id.in_(related_ids),
                               Snapshot.child_type == asmnt.assessment_type,
                           )).alias("objects_mapped")
        return db.session.query(
            objects_mapped.c.obj_id.label("obj_id"),
            objects_mapped.c.obj_type.label("obj_type"))

    @classmethod
    def mapped_objs(cls, object_type, object_id, same_type_mapped=False):
        """Find all instances that have relationship with provided object.

    Args:
        object_type: Type of object (can be str or SQLAlchemy property).
        object_id: Id of object (can be int or SQLAlchemy property).
        same_type_mapped: If True - related objects with same type only
            will be searched.

    Returns:
        SQLAlchemy query with id and type of found
        objects [(obj_id, obj_type)].
    """
        source_rel = db.session.query(
            Relationship.source_id.label("obj_id"),
            Relationship.source_type.label("obj_type"),
            Relationship.destination_type.label("base_type"),
        ).filter(
            Relationship.destination_type == object_type,
            Relationship.destination_id == object_id,
        )

        destination_rel = db.session.query(
            Relationship.destination_id,
            Relationship.destination_type,
            Relationship.source_type,
        ).filter(
            Relationship.source_type == object_type,
            Relationship.source_id == object_id,
        )

        if same_type_mapped:
            source_rel = source_rel.filter(
                Relationship.source_type == Relationship.destination_type)
            destination_rel = destination_rel.filter(
                Relationship.source_type == Relationship.destination_type)
        return sa.union_all(source_rel,
                            destination_rel).alias("mapped_related")

    @classmethod
    def mapped_to_obj_snapshot(cls, object_type, object_id):
        """Find all instances that have relationship with snapshot of object.

    Args:
        object_type: Type of object (can be str or SQLAlchemy property).
        object_id: Id of object (can be int or SQLAlchemy property).

    Returns:
        List of SQLAlchemy queries that yields results
        [(similar_id, similar_type, related_type)] - the id, type of similar
        objects and object type they linked through.
    """
        source_query = db.session.query(
            Relationship.destination_id.label("similar_id"),
            Relationship.destination_type.label("similar_type"),
            Snapshot.child_type.label("related_type"),
        ).join(Snapshot,
               sa.and_(
                   Relationship.source_id == Snapshot.id,
                   Relationship.source_type == Snapshot.__name__,
               )).filter(
                   Snapshot.child_type == object_type,
                   Snapshot.child_id == object_id,
               )

        destination_query = db.session.query(
            Relationship.source_id.label("similar_id"),
            Relationship.source_type.label("similar_id"),
            Snapshot.child_type.label("related_type"),
        ).join(Snapshot,
               sa.and_(
                   Relationship.destination_id == Snapshot.id,
                   Relationship.destination_type == Snapshot.__name__,
               )).filter(
                   Snapshot.child_type == object_type,
                   Snapshot.child_id == object_id,
               )

        return [source_query, destination_query]
