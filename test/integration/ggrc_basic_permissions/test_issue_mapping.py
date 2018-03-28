# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Test Mapping Issue mapping"""

from ddt import data, ddt, unpack
from ggrc.app import app  # NOQA pylint: disable=unused-import
from ggrc.models import all_models
from integration.ggrc import TestCase
from integration.ggrc.api_helper import Api
from integration.ggrc.models import factories
from integration.ggrc_basic_permissions.models \
    import factories as rbac_factories


def _get_map_dict(destination, source):
    return {
        'relationship': {
            "context": {
                "id": destination.context.id,
                "type": "Context"
            },
            "source": {
                "id": source.id,
                "type": source.type
            },
            "destination": {
                "id": destination.id,
                "type": destination.type
            }
        }
    }


@ddt
class TestIssueMapping(TestCase):
    """Test Issue mapping"""

    def setup_roles(self):
        """Setup necessary roles needed by the tests"""
        query = all_models.Role.query
        acr_query = all_models.AccessControlRole.query
        self.roles = {
            'creator':
            query.filter_by(name="Creator").first(),
            'auditors':
            acr_query.filter_by(name="Auditors").first(),
            'program_editors':
            acr_query.filter_by(name="Program Editors Mapped").first()
        }

    def setup_users(self):
        """Creates two creator users"""
        self.users = {}
        for user_name in ('auditor', 'programeditor'):
            user = factories.PersonFactory()
            rbac_factories.UserRoleFactory(
                role=self.roles['creator'], person=user)
            self.users[user_name] = user

    def setup_audits(self):
        """Create an audit and an archived audit"""
        self.audits = {
            False: self.create_audit(archived=False),
            True: self.create_audit(archived=True)
        }

    def setup_snapshots_and_issue(self):
        """Create snapshot & issue objects"""
        self.snapshots = {}
        self.issues = {}
        self.control = factories.ControlFactory()
        revision = all_models.Revision.query.filter(
            all_models.Revision.resource_type == self.control.type).first()
        for is_archived in (False, True):
            audit = self.audits[is_archived]
            # Create a snapshot
            self.snapshots[is_archived] = factories.SnapshotFactory(
                child_id=revision.resource_id,
                child_type=revision.resource_type,
                revision=revision,
                parent=audit,
                context=audit.context,
            )
            # Create an issue
            issue = factories.IssueFactory()
            self.issues[is_archived] = issue
            # Map issue to audit
            factories.RelationshipFactory(
                source=audit, destination=issue, context=audit.context)

    def create_audit(self, archived=False):
        """Create an audit object and fix the it's context"""
        audit = factories.AuditFactory(archived=archived)

        # Add auditor & program editor roles
        factories.AccessControlListFactory(
            ac_role=self.roles['auditors'],
            object=audit,
            person=self.users['auditor'])
        factories.AccessControlListFactory(
            ac_role=self.roles['program_editors'],
            object=audit,
            person=self.users['programeditor'])

        return audit

    def setUp(self):
        """Prepare data needed to run the tests"""
        self.api = Api()
        self.setup_roles()
        self.setup_users()
        self.setup_audits()
        self.setup_snapshots_and_issue()

    @data(
        # user_name, is_archived
        ('auditor', True),
        ('programeditor', True),
        ('auditor', False),
        ('programeditor', False),
    )
    @unpack
    def test_mapping_to_issue(self, user_name, is_archived):
        """Test mapping snapshots to issue"""
        user = self.users[user_name]
        payload = _get_map_dict(self.snapshots[is_archived],
                                self.issues[is_archived])
        self.api.set_user(user)

        # Try to map to audit
        response = self.api.post(all_models.Relationship, payload)
        self.assertStatus(response, 201)

        rel_id = response.json['relationship']['id']
        relationship = all_models.Relationship.query.filter_by(
            id=rel_id).first()
        response = self.api.delete(relationship)
        self.assertStatus(response, 200)
