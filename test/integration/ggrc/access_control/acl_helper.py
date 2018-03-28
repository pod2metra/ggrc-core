# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Helper functions for ACL testing."""


def get_acl_json(role_id, person_id):
    """Helper function for setting ACL json."""
    return {
        "ac_role_id": role_id,
        "person": {
            "type": "Person",
            "id": person_id
        }
    }


def get_acl_list(pid_acr_mapping):
    """Helper function for formatting ACL json list."""
    return [
        get_acl_json(role_id, person_id)
        for person_id, role_id in pid_acr_mapping.iteritems()
    ]
