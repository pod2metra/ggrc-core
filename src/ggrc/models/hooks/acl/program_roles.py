# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""All hooks required by program acl roles business cases

Program Readers, Program Editors, Program Managers acl roles get propagated to:
- Mapped objects (through relationships)
  - Comments & Documents
- Audit
  - Assessment Templates
  - Snapshots
  - Assessments
    - Comments & Documents
  - Issues
    - Comments & Documents
"""

from sqlalchemy.orm import load_only

from ggrc.models import all_models
from ggrc.models.hooks.acl.acl_manager import ACLManager
from ggrc.models.relationship import Stub, RelationshipsCache
from ggrc.models.hooks.relationship import related

# The dictionary below describes how program roles (Program Managers, Program
# Editors and Program Readers) propagate to mapped objects.
PROGRAM_ACL_PROPAGATION_RULES = {
    "roles": {"Program Managers", "Program Readers", "Program Editors"},
    "relationships": {
        "type": "any",
        "propagate": {
            "roles": {
                "Program Managers Mapped", "Program Readers Mapped",
                "Program Editors Mapped"
            },
            "relationships": {
                "type": "Comment,Document"
            }
        }
    },
    "audits": {
        "propagate": {
            "roles": {
                "Program Managers Mapped", "Program Readers Mapped",
                "Program Editors Mapped"
            },
            "relationships": {
                "type": "Assessment,Issue,AssessmentTemplate",
                "propagate": {
                    "roles": {
                        "Program Managers Mapped", "Program Readers Mapped",
                        "Program Editors Mapped"
                    },
                    "relationships": {
                        "type": "Comment,Document"
                    }
                }
            },
            "snapshots": {}
        }
    }
}

# Role propagation
ROLE_PROPAGATION = {
    "Program Managers": "Program Managers Mapped",
    "Program Editors": "Program Editors Mapped",
    "Program Readers": "Program Readers Mapped",
    "Program Managers Mapped": "Program Managers Mapped",
    "Program Editors Mapped": "Program Editors Mapped",
    "Program Readers Mapped": "Program Readers Mapped",
}


def _get_acr_id(acl):
    """Get acr id from acl object"""
    if acl.ac_role_id is not None:
        return acl.ac_role_id
    if acl.ac_role is not None:
        return acl.ac_role.id
    return None


def related_to(rel, types):
    """Related to helper"""
    source, destination = rel.source, rel.destination
    if source.type in types:
        return source, destination
    elif destination.type in types:
        return destination, source
    return None, None


def _get_program_roles():
    """Get a dict of program roles"""
    roles = all_models.AccessControlRole.query.filter().options(
        load_only("id", "name")).all()
    res = {role.name: role.id for role in roles}
    res.update({role.id: role.name for role in roles})
    return res


class ProgramRolesHandler(object):
    """Handle program role propagation"""

    def __init__(self):
        self.access_control_list_manager = None
        self.relationship_cache = None
        self.program_roles = None
        self.done = set()

    def handle_snapshots(self, _, acl):
        """Handle audit propagation"""
        acl_manager = self.access_control_list_manager
        audit = acl.object
        # When role propagation is migrated to sql steatements and the
        # aduit.snapshotted_objects line is removed, the Snapshotable mixin can
        # be removed as well.
        for snapshot in audit.snapshotted_objects:
            acl_manager.get_or_create(snapshot, acl, acl.person,
                                      acl.ac_role_id)

    def _get_acr_name(self, acl):
        """Helper for retrieving access control name"""
        role_map = self.program_roles
        id_ = _get_acr_id(acl)
        return role_map[id_]

    def handle_audits(self, propagation, acl):
        """Handle audit propagation"""
        role_map = self.program_roles
        acl_manager = self.access_control_list_manager
        for audit in acl.object.audits:
            child = acl_manager.get_or_create(
                audit, acl, acl.person,
                role_map[ROLE_PROPAGATION[self._get_acr_name(acl)]])
            if "propagate" in propagation:
                self.handle_propagation(propagation["propagate"], child)

    def handle_relationships(self, propagation, acl):
        """Hanle relationships"""
        relationship_cache = self.relationship_cache
        role_map = self.program_roles
        acl_manager = self.access_control_list_manager
        program_stub = Stub(acl.object_type, acl.object_id)
        related_stubs = related([program_stub], relationship_cache)
        for stub in related_stubs[program_stub]:
            if not (propagation["type"] == "any"
                    or stub.type in propagation["type"].split(",")):
                continue
            role_id = role_map[ROLE_PROPAGATION[self._get_acr_name(acl)]]
            child = acl_manager.get_or_create(stub, acl, acl.person, role_id)
            if "propagate" in propagation:
                self.handle_propagation(propagation["propagate"], child)

    def handle_propagation(self, propagation, acl):
        """Handle propagation dict"""
        name = self._get_acr_name(acl)
        if name not in propagation["roles"]:
            return
        if "relationships" in propagation:
            self.handle_relationships(propagation["relationships"], acl)
        if "audits" in propagation:
            self.handle_audits(propagation["audits"], acl)
        if "snapshots" in propagation:
            self.handle_snapshots(propagation["snapshots"], acl)

    def handle_access_control_list(self, obj):
        """Handle PROGRAM_ACL_PROPAGATION_RULES dict to create all needed
       propagations"""
        self.handle_propagation(PROGRAM_ACL_PROPAGATION_RULES, obj)

    def handle_snapshot(self, obj):
        """When a snapshot is created propagate program roles"""
        access_control_list = obj.parent.full_access_control_list
        for acl in access_control_list:
            if acl.ac_role.name not in {
                    "Program Readers Mapped", "Program Editors Mapped",
                    "Program Managers Mapped"
            }:
                continue
            acl_manager = self.access_control_list_manager
            acl_manager.get_or_create(obj, acl, acl.person, acl.ac_role.id)

    def handle_relationship_creation(self, obj):
        """Handle relationship creation"""
        acl_manager = self.access_control_list_manager
        role_map = self.program_roles
        program, other = related_to(obj, "Program")
        if program:
            for acl in program.access_control_list:
                role_name = self._get_acr_name(acl)
                if role_name not in {
                        "Program Readers", "Program Editors",
                        "Program Managers"
                }:
                    continue

                acl_manager.get_or_create(
                    other, acl, acl.person,
                    role_map[ROLE_PROPAGATION[self._get_acr_name(acl)]])
            return

        for related_object in ("Audit", "Assessment", "Issue"):
            parent, other = related_to(obj, related_object)
            if parent:
                for acl in parent.full_access_control_list:
                    if self._get_acr_name(acl) not in {
                            "Program Readers Mapped", "Program Editors Mapped",
                            "Program Managers Mapped"
                    }:
                        continue
                    acl_manager.get_or_create(other, acl, acl.person,
                                              _get_acr_id(acl))
                return

    def handle_audit_creation(self, obj):
        """Propagate roles when audit is created or cloned"""
        acl_manager = self.access_control_list_manager
        role_map = self.program_roles
        for acl in obj.program.access_control_list:
            role_name = self._get_acr_name(acl)
            if role_name not in {
                    "Program Readers", "Program Editors", "Program Managers"
            }:
                continue
            acl_manager.get_or_create(
                obj, acl, acl.person,
                role_map[ROLE_PROPAGATION[self._get_acr_name(acl)]])

    def after_flush(self, session):
        """Handle program related acl"""
        self.access_control_list_manager = ACLManager()
        self.relationship_cache = RelationshipsCache()
        self.program_roles = _get_program_roles()

        handlers = {
            all_models.AccessControlList: self.handle_access_control_list,
            all_models.Snapshot: self.handle_snapshot,
            all_models.Relationship: self.handle_relationship_creation,
            all_models.Audit: self.handle_audit_creation
        }
        for obj in session.new:
            handler = handlers.get(type(obj))
            if callable(handler):
                if obj not in self.done:
                    handler(obj)
                    self.done.add(obj)
