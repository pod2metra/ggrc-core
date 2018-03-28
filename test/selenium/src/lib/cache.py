# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Module containing various caches"""

from lib.constants import element


def _get_lhn_section_map():
    """Return dictionary with lhn elements that are grouped together
 into sections
 Return:
      dict
 """
    members_dct = {}
    member_tpls = ((element.Lhn.DIRECTIVES, element.Lhn.DIRECTIVES_MEMBERS),
                   (element.Lhn.CONTROLS_OR_OBJECTIVES,
                    element.Lhn.CONTROLS_OR_OBJECTIVES_MEMBERS),
                   (element.Lhn.PEOPLE_OR_GROUPS,
                    element.Lhn.PEOPLE_OR_GROUPS_MEMBERS),
                   (element.Lhn.ASSETS_OR_BUSINESS,
                    element.Lhn.ASSETS_OR_BUSINESS_MEMBERS),
                   (element.Lhn.RISKS_OR_THREATS,
                    element.Lhn.RISKS_OR_THREATS_MEMBERS))

    for section, members in member_tpls:
        members_dct.update({member: section for member in members})

    return members_dct


LHN_SECTION_MEMBERS = _get_lhn_section_map()
