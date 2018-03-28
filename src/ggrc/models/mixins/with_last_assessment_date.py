# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Contains WithLastAssessmentDate mixin.

This defines logic to get finished_date fields of the last Assessment over all
Snapshots of self.
"""

from ggrc.fulltext import attributes
from ggrc.builder import simple_property
from ggrc.models import reflection
from ggrc.models.mixins import attributable


class WithLastAssessmentDate(attributable.Attributable):
    """Defines logic to get max finished_date of all Asmts over own Snapshots."""
    # pylint: disable=too-few-public-methods

    _api_attrs = reflection.ApiAttributes(
        reflection.Attribute(
            "last_assessment_date", create=False, update=False), )

    _aliases = {
        "last_assessment_date": {
            "display_name": "Last Assessment Date",
            "view_only": True,
        },
    }

    _fulltext_attrs = [
        attributes.DatetimeFullTextAttr("last_assessment_date",
                                        "last_assessment_date")
    ]

    @simple_property
    def last_assessment_date(self):
        lad_attr = self.attributes.get("last_assessment_date")
        return lad_attr.value_datetime if lad_attr else None
