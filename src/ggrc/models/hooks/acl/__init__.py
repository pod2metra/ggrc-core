# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Entry point for all acl handlers.

This package should have the single hook that should handle all acl propagation
and deletion.
"""

import sqlalchemy as sa
from sqlalchemy.orm.session import Session

from ggrc.models.hooks.acl import audit_roles
from ggrc.models.hooks.acl import program_roles
from ggrc.models.hooks.acl import relationship_deletion
from ggrc.models.hooks import access_control_list
from ggrc.models.hooks import relationship
from ggrc_workflows.models.hooks import workflow


def after_flush(session, _):
    """Handle all ACL hooks after after flush."""

    relationship.handle_relationship_creation(session)
    access_control_list.handle_acl_creation(session)
    program_role_handler = program_roles.ProgramRolesHandler()
    program_role_handler.after_flush(session)
    audit_role_handler = audit_roles.AuditRolesHandler()
    audit_role_handler.after_flush(session)
    relationship_deletion.after_flush(session)
    workflow.handle_acl_changes(session)


def init_hook():
    """Initialize Relationship-related hooks."""
    sa.event.listen(Session, "after_flush", after_flush)
