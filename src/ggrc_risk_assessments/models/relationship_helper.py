# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

from ggrc import db
from ggrc_risk_assessments.models import RiskAssessment


def ra_person(object_type, related_type, related_ids):
    if {object_type, related_type} != {"RiskAssessment", "Person"}:
        return None
    if object_type == "Person":
        return db.session \
            .query(RiskAssessment.ra_manager_id) \
            .filter(RiskAssessment.id.in_(related_ids)) \
            .union(
                db.session.query(RiskAssessment.ra_counsel_id)
                          .filter(RiskAssessment.id.in_(related_ids))
            )
    else:
        return db.session \
            .query(RiskAssessment.id) \
            .filter(
                (RiskAssessment.ra_manager_id.in_(related_ids)) |
                (RiskAssessment.ra_counsel_id.in_(related_ids))
            )


def get_ids_related_to(object_type, related_type, related_ids):
    functions = [ra_person]
    queries = (f(object_type, related_type, related_ids) for f in functions)
    non_empty = [q for q in queries if q]
    if len(non_empty) == 0:
        return None
    return non_empty.pop().union(*non_empty)
