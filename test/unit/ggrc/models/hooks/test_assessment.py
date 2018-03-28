# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Test assessment hooks."""

import unittest

import ddt
import mock

from ggrc.models.hooks import assessment


@ddt.ddt
class TestFromSession(unittest.TestCase):
    """Test session-listener wrapper.

  Models are substituted with builtin types as they can be used for
  isinstance checks too.
  """

    def setUp(self):
        super(TestFromSession, self).setUp()
        self.session = mock.Mock()

    @ddt.data(
        ([], {
            'Auditors': [],
            'Audit Lead': []
        }),
        ([{
            "ac_role_id": 5,
            "person_id": 1
        }], {
            'Auditors': [],
            'Audit Lead': []
        }),
        ([{
            "ac_role_id": 1,
            "person_id": 1
        }], {
            'Auditors': [1],
            'Audit Lead': []
        }),
        (
            [
                {
                    "ac_role_id": 1,
                    "person_id": 1
                },
                {
                    "ac_role_id": 5,
                    "person_id": 2
                },
                {
                    "ac_role_id": 6,
                    "person_id": 3
                },
            ],
            {
                'Auditors': [1],
                'Audit Lead': []
            },
        ),
    )
    @ddt.unpack
    def test_generate_role_object_dict(self, content_acl, expected):
        """Generate role object should not fail on a missing role for

    This test checks that any role can be missing and the roles dict is still
    returned. This is okay if the missing roles are editable, this test does
    not check that we actually can't remove non-editable roles.
    """
        mock_path = "ggrc.access_control.role.get_custom_roles_for"
        with mock.patch(mock_path) as roles_mock:
            roles_mock.return_value = {
                1: "Auditors",
                2: "Audit Captains",
            }
            assessment.logger = mock.MagicMock()
            audit = mock.MagicMock()
            audit.access_control_list = []
            snapshot = mock.MagicMock()
            snapshot.revision.content = {
                "access_control_list": content_acl,
            }
            acl_dict = assessment.generate_role_object_dict(snapshot, audit)
            self.assertEqual(acl_dict, expected)
