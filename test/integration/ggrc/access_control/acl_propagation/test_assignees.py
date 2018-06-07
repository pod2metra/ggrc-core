# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Test Access Control roles Assignees propagation"""

import ddt

from ggrc.models import all_models
from integration.ggrc.access_control import rbac_factories
from integration.ggrc.access_control.acl_propagation import base
from integration.ggrc.test_utils import helpers


@ddt.ddt
class TestAssigneesPropagation(base.TestACLPropagation):
  """Test Assignees role permissions propagation"""

  PERMISSIONS = {
      "Creator": {
          "Assessment": {
              "create": False,
              "read": True,
              "update": True,
              "delete": False,
              "map_snapshot": False,
              "read_revisions": True,
              "deprecate": True,
              "complete": True,
              "in_progress": True,
              "not_started": True,
              "decline": (False, "unimplemented"),
              "verify": (False, "unimplemented"),
              "map_comment": True,
              "map_evidence": True,
              "related_assessments": True,
              "related_objects": True,
          },
          "Snapshot Assessment": {
              "read": True,
              "read_original": False,
              "update": False,
              "get_latest_version": False,
          },
          "Snapshot Audit": {
              "read": False,
              "read_original": False,
              "update": False,
              "get_latest_version": False,
          },
          "Issue Assessment": {
              "read": True,
              "update": True,
              "delete": True,
              "read_revisions": True,
              "map": False,
              "create_and_map": True,
              "raise_issue": True,
              "unmap": True,
          },
          "Issue Audit": {
              "read": False,
              "update": False,
              "delete": False,
              "read_revisions": False,
              "map": False,
              "create_and_map": False,
              "unmap": False,
          },
          "Evidence Audit": {
              "create_and_map": False,
              "read": True,
              "update": False,
              "delete": False,
              "read_comments": True,
              "add_comment": False
          },
          "Evidence Assessment": {
              "create_and_map": True,
              "read": True,
              "update": True,
              "delete": False,
              "read_comments": True,
              "add_comment": True
          }
      },
      "Reader": {
          "Assessment": {
              "read": True,
              "update": True,
              "delete": False,
              "map_snapshot": False,
              "read_revisions": True,
              "deprecate": True,
              "complete": True,
              "in_progress": True,
              "not_started": True,
              "decline": (False, "unimplemented"),
              "verify": (False, "unimplemented"),
              "map_comment": True,
              "map_evidence": True,
              "related_assessments": True,
              "related_objects": True,
          },
          "Snapshot Assessment": {
              "read": True,
              "read_original": True,
              "update": False,
              "get_latest_version": True,
          },
          "Snapshot Audit": {
              "read": True,
              "read_original": True,
              "update": False,
              "get_latest_version": True,
          },
          "Issue Assessment": {
              "read": True,
              "update": True,
              "delete": True,
              "read_revisions": True,
              "map": False,
              "create_and_map": True,
              "raise_issue": True,
              "unmap": True,
          },
          "Issue Audit": {
              "read": True,
              "update": False,
              "delete": False,
              "read_revisions": True,
              "map": False,
              "create_and_map": False,
              "unmap": False,
          },
          "Evidence Audit": {
              "create_and_map": False,
              "read": True,
              "update": False,
              "delete": False,
              "add_comment": False,
              "read_comments": True
          },
          "Evidence Assessment": {
              "create_and_map": True,
              "read": True,
              "update": True,
              "delete": False,
              "add_comment": True,
              "read_comments": True
          }
      },
      "Editor": {
          "Assessment": {
              "read": True,
              "update": True,
              "delete": True,
              "map_snapshot": True,
              "read_revisions": True,
              "deprecate": True,
              "complete": True,
              "in_progress": True,
              "not_started": True,
              "decline": (False, "unimplemented"),
              "verify": (False, "unimplemented"),
              "map_comment": True,
              "map_evidence": True,
              "related_assessments": True,
              "related_objects": True,
          },
          "Snapshot Assessment": {
              "read": True,
              "read_original": True,
              "update": True,
              "get_latest_version": True,
          },
          "Snapshot Audit": {
              "read": True,
              "read_original": True,
              "update": True,
              "get_latest_version": True,
          },
          "Issue Assessment": {
              "read": True,
              "update": True,
              "delete": True,
              "read_revisions": True,
              "map": True,
              "create_and_map": True,
              "raise_issue": True,
              "unmap": True,
          },
          "Issue Audit": {
              "read": True,
              "update": True,
              "delete": True,
              "read_revisions": True,
              "map": True,
              "create_and_map": True,
              "unmap": True,
          },
          "Evidence Audit": {
              "create_and_map": True,
              "read": True,
              "update": True,
              "delete": False,
              "read_comments": True,
              "add_comment": True,
          },
          "Evidence Assessment": {
              "create_and_map": True,
              "read": True,
              "update": True,
              "delete": False,
              "read_comments": True,
              "add_comment": True,
          }
      },
  }

  def init_factory(self, role, model, parent):
    """Initialize RBAC factory with propagated Assignees role.

    Args:
        role: Global Custom role that user have (Creator/Reader/Editor).
        model: Model name for which factory should be got.
        parent: Model name in scope of which objects should be installed.

    Returns:
        Initialized RBACFactory object.
    """
    self.setup_people()
    assignees_acr = all_models.AccessControlRole.query.filter_by(
        name="Assignees",
        object_type="Assessment",
    ).first()

    rbac_factory = rbac_factories.get_factory(model)
    return rbac_factory(self.people[role].id, assignees_acr, parent)

  @helpers.unwrap(PERMISSIONS)
  def test_access(self, role, model, action_name, expected_result):
    """Assignees {0:<7}: On {1:<20} test {2:<20} - Expected {3:<2} """
    self.runtest(role, model, action_name, expected_result)
