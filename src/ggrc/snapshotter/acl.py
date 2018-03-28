# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Handle acl"""

from sqlalchemy.sql.expression import tuple_

from ggrc import db
from ggrc.models import all_models


def get_acl_payload(snapshots):
    """Get ACL payload for newly created snapshots"""
    acl_payload = []
    parents = set(
        (snapshot.parent_id, snapshot.parent_type) for snapshot in snapshots)
    ac_roles = db.session.query(
        all_models.AccessControlRole.id,
        all_models.AccessControlRole.name).filter(
            all_models.AccessControlRole.name.in_(
                ("Auditors", "Audit Captains", "Auditors Snapshot Mapped",
                 "Audit Captains Mapped", "Program Managers Mapped",
                 "Program Editors Mapped", "Program Readers Mapped")))
    ac_roles = {name: id_ for id_, name in ac_roles}
    parent_roles = db.session.query(
        all_models.AccessControlList.id,
        all_models.AccessControlList.person_id,
        all_models.AccessControlList.ac_role_id).filter(
            all_models.AccessControlList.ac_role_id.in_(
                (ac_roles["Auditors"], ac_roles["Audit Captains"],
                 ac_roles["Program Managers Mapped"],
                 ac_roles["Program Editors Mapped"],
                 ac_roles["Program Readers Mapped"])),
            tuple_(all_models.AccessControlList.object_id,
                   all_models.AccessControlList.object_type).in_(parents))
    child_roles = {
        ac_roles["Auditors"]: ac_roles["Auditors Snapshot Mapped"],
        ac_roles["Audit Captains"]: ac_roles["Audit Captains Mapped"],
        ac_roles["Program Managers Mapped"]:
        ac_roles["Program Managers Mapped"],
        ac_roles["Program Editors Mapped"]: ac_roles["Program Editors Mapped"],
        ac_roles["Program Readers Mapped"]: ac_roles["Program Readers Mapped"],
    }
    for parent_id, person_id, ac_role_id in parent_roles:
        for snapshot in snapshots:
            acl_payload.append({
                "object_id": snapshot.id,
                "object_type": "Snapshot",
                "ac_role_id": child_roles[ac_role_id],
                "parent_id": parent_id,
                "person_id": person_id
            })
    return acl_payload
