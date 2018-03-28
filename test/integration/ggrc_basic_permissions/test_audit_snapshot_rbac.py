# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Test audit RBAC"""

import itertools

from os.path import abspath
from os.path import dirname
from os.path import join
from collections import defaultdict
from integration.ggrc import TestCase
from integration.ggrc.api_helper import Api

import integration.ggrc.generator

from ggrc import db
from ggrc.models import all_models

DEFAULT_LACK_OF_PERMISSIONS = {"Snapshot": 403, "Audit": 403}
DEFAULT_AUDITOR_PERMISSIONS = {"Snapshot": 200, "Audit": 403}


class TestAuditRBAC(TestCase):
    """Test audit RBAC"""
    # pylint: disable=too-many-instance-attributes

    CSV_DIR = join(abspath(dirname(__file__)), "test_csvs")

    def setUp(self):
        """Imports test_csvs/audit_rbac_snapshot_create.csv needed by the tests"""
        TestCase.clear_data()
        self.api = Api()
        self.objgen = integration.ggrc.generator.ObjectGenerator()

        self.csv_files = itertools.cycle([
            "audit_rbac_snapshot_create.csv", "audit_rbac_snapshot_update.csv"
        ])

        response = self._import_file(next(self.csv_files))
        self._check_csv_response(response, {})

        self.people = all_models.Person.eager_query().all()

        self.auditor_role = all_models.AccessControlRole.query.filter(
            all_models.AccessControlRole.name == "Auditors").one()

        self.program = db.session.query(all_models.Program).filter(
            all_models.Program.slug == "PMRBACPROGRAM-1").one()

        sources = set(r.source for r in self.program.related_sources)
        destinations = set(
            r.destination for r in self.program.related_destinations)
        related = [
            obj for obj in sources.union(destinations)
            if not isinstance(obj, all_models.Person)
        ]
        self.related_objects = related

        self.api = Api()
        self.client.get("/login")

        self.audit = self.create_audit()

        self.snapshots = all_models.Snapshot.eager_query().all()

    def create_audit(self):
        """Create default audit for audit snapshot RBAC tests"""
        people = {person.email: person for person in self.people}
        auditor_emails = [
            "readerauditor@test.com",
            "creatorauditor@test.com",
            "editorauditor@test.com",
            "adminauditor@test.com",
        ]
        _, audit = self.objgen.generate_object(
            all_models.Audit, {
                "title":
                "Snapshotable audit",
                "program": {
                    "id": self.program.id
                },
                "status":
                "Planned",
                "snapshots": {
                    "operation": "create",
                },
                "access_control_list": [{
                    "ac_role_id": self.auditor_role.id,
                    "person": {
                        "id": people[person].id,
                        "type": "Person"
                    }
                } for person in auditor_emails],
                "context": {
                    "type": "Context",
                    "id": self.program.context_id,
                    "href": "/api/contexts/{}".format(self.program.context_id)
                }
            })
        return audit

    def update_audit(self):
        """Update default audit"""
        response = self._import_file(next(self.csv_files))
        self._check_csv_response(response, {})

        audit = all_models.Audit.query.filter(
            all_models.Audit.title == "Snapshotable audit").one()
        self.audit = audit

        self.api.modify_object(self.audit,
                               {"snapshots": {
                                   "operation": "upsert"
                               }})

    def read(self, objects):
        """Attempt to do a GET request for every object in the objects list"""
        responses = []
        for obj in objects:
            status_code = self.api.get(obj.__class__, obj.id).status_code
            responses.append((obj.type, status_code))
        return responses

    def update(self, objects):
        """Attempt to do a PUT request for every object in the objects list"""
        scope_response = self.api.get(self.audit.__class__, self.audit.id)
        if scope_response.status_code == 200:
            self.update_audit()

        responses = []
        for obj in objects:
            response = self.api.get(obj.__class__, obj.id)
            status_code = response.status_code
            if response.status_code == 200:
                data = response.json
                if obj.type == "Snapshot":
                    data.update({"update_revision": "latest"})
                put_call = self.api.put(obj, data)
                status_code = put_call.status_code
            responses.append((obj.type, status_code))
        return responses

    def call_api(self, method, expected_statuses):
        """Calls the REST api with a given method and returns a list of
       status_codes that do not match the expected_statuses dict"""
        all_errors = []
        for person in self.people:
            self.api.set_user(person)
            responses = method(self.snapshots + [self.audit])
            for type_, code in responses:
                if code != expected_statuses[person.email][type_]:
                    all_errors.append(
                        "{} does not have {} access to {} ({})".format(
                            person.email, method.__name__, type_, code))
        return all_errors

    def test_read_access_on_mapped(self):
        """Test READ access to snapshotted objects of default audit"""
        expected_statuses = defaultdict(lambda: defaultdict(lambda: 200))
        exceptional_users = (("creator@test.com",
                              DEFAULT_LACK_OF_PERMISSIONS), )
        for user, exceptions in exceptional_users:
            for type_, status_code in exceptions.items():
                expected_statuses[user][type_] = status_code
        errors = self.call_api(self.read, expected_statuses)
        assert not errors, "\n".join(errors)

    def test_update_access_on_mapped(self):
        """Test UPDATE access to snapshotted objects of default audit"""
        expected_statuses = defaultdict(lambda: defaultdict(lambda: 200))

        exceptional_users = (
            ("creator@test.com", DEFAULT_LACK_OF_PERMISSIONS),
            ("reader@test.com", DEFAULT_LACK_OF_PERMISSIONS),
            ("creatorpr@test.com", DEFAULT_LACK_OF_PERMISSIONS),
            ("readerpr@test.com", DEFAULT_LACK_OF_PERMISSIONS),
            # Auditor roles
            ("readerauditor@test.com", DEFAULT_AUDITOR_PERMISSIONS),
            ("creatorauditor@test.com", DEFAULT_AUDITOR_PERMISSIONS))

        for user, exceptions in exceptional_users:
            for type_, status_code in exceptions.items():
                expected_statuses[user][type_] = status_code

        errors = self.call_api(self.update, expected_statuses)
        assert not errors, "\n".join(errors)
