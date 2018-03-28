# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Module for direct audit relationships mixin."""

from ggrc.models.audit import Audit
from ggrc.models.relationship import Relationship


class AuditRelationship(object):
    # pylint: disable=too-few-public-methods
    """Mixin for mandatory link to an Audit via Relationships."""

    _aliases = {
        "audit": {
            "display_name": "Audit",
            "mandatory": True,
            "filter_by": "_filter_by_audit",
            "ignore_on_update": True,
        },
    }

    @classmethod
    def _filter_by_audit(cls, predicate):
        """Get filter for objects related to an Audit."""
        return Relationship.query.filter(
            Relationship.source_type == cls.__name__,
            Relationship.source_id == cls.id,
            Relationship.destination_type == Audit.__name__,
        ).join(Audit, Relationship.destination_id == Audit.id).filter(
            predicate(Audit.slug)).exists() | Relationship.query.filter(
                Relationship.destination_type == cls.__name__,
                Relationship.destination_id == cls.id,
                Relationship.source_type == Audit.__name__,
            ).join(Audit, Relationship.source_id == Audit.id).filter(
                predicate(Audit.slug)).exists()
