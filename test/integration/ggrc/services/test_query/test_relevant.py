# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Tests for relevant operator."""

import collections

import ddt

from ggrc.models import all_models

from integration.ggrc import TestCase
from integration.ggrc.query_helper import WithQueryApi
from integration.ggrc.models import factories


@ddt.ddt
class TestRelevant(TestCase, WithQueryApi):
    """Tests for relevant queries.

  The relevant query is an extension of the related operation in the way that
  it also includes special mappings not just the relationships table.
  """

    PEOPLE = [
        # Role name, email, expected count
        ("auditor", "auditor@example.com", 0),
        ("program_editor", "program_editor@example.com", 0),
        ("assignee", "assignee@example.com", 1),
    ]

    def setUp(self):
        super(TestRelevant, self).setUp()
        self.client.get("/login")
        roles = collections.defaultdict(dict)
        roles_query = all_models.AccessControlRole.query.filter(
            all_models.AccessControlRole.object_type.in_([
                all_models.Assessment.__name__,
                all_models.Audit.__name__,
                all_models.Program.__name__,
            ]))

        for role in roles_query:
            roles[role.object_type][role.name] = role

        with factories.single_commit():
            assessment = factories.AssessmentFactory()
            factories.RelationshipFactory(
                source=assessment.audit,
                destination=assessment,
            )
            people = {}
            for person in self.PEOPLE:
                people[person[0]] = factories.PersonFactory(email=person[1])
            # Correct roles and propagation for a given assessment
            factories.AccessControlListFactory(
                ac_role=roles["Assessment"]["Assignees"],
                person=people["assignee"],
                object=assessment,
            )
            factories.AccessControlListFactory(
                ac_role=roles["Audit"]["Auditors"],
                person=people["auditor"],
                object=assessment.audit,
            )
            factories.AccessControlListFactory(
                ac_role=roles["Program"]["Program Editors"],
                person=people["program_editor"],
                object=assessment.audit.program,
            )

    @ddt.data(*PEOPLE)
    @ddt.unpack
    def test_person_relevant(self, role, email, expected_count):
        """Check that only assessment roles can see relevant assessments"""
        person = all_models.Person.query.filter(
            all_models.Person.email == email).one()

        ids = self._get_first_result_set({
            "object_name": "Assessment",
            "type": "ids",
            "filters": {
                "expression": {
                    "object_name": "Person",
                    "op": {
                        "name": "relevant"
                    },
                    "ids": [person.id]
                }
            }
        }, "Assessment", "ids")
        self.assertEqual(
            len(ids), expected_count,
            "Invalid relevant assessments count ({} instead of {}) for {}.".
            format(
                len(ids),
                expected_count,
                role,
            ))
