# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Tests for /api/related_assessments endpoint.

These tests only check the data returned by related assessments endpoint.
There are other tests for verifying completeness of the results and that focus
more on verifying the related SQL query.
"""

import mock
import ddt

from ggrc import views
from integration.ggrc.models import factories
from integration.ggrc.services import TestCase


@ddt.ddt
class TestRelatedAssessments(TestCase):
    """Tests for special people api endpoints."""

    URL_BASE = "/api/related_assessments"

    def setUp(self):
        super(TestRelatedAssessments, self).setUp()
        self.client.get("/login")
        with factories.single_commit():
            self.assessment1 = factories.AssessmentFactory(title="A_1")
            self.assessment2 = factories.AssessmentFactory(title="A_2")
            self.control = factories.ControlFactory()
            snap1 = self._create_snapshots(self.assessment1.audit,
                                           [self.control])
            snap2 = self._create_snapshots(self.assessment2.audit,
                                           [self.control])
            factories.RelationshipFactory(
                source=snap1[0], destination=self.assessment1)
            factories.RelationshipFactory(
                destination=snap2[0],
                source=self.assessment2,
            )
            factories.RelationshipFactory(
                source=self.assessment1.audit,
                destination=self.assessment1,
            )
            factories.RelationshipFactory(
                destination=self.assessment2.audit,
                source=self.assessment2,
            )

    def _get_related_assessments(self, obj, **kwargs):
        """Helper for retrieving assessment related objects."""
        kwargs["object_type"] = obj.type
        kwargs["object_id"] = obj.id
        return self.client.get(self.URL_BASE, query_string=kwargs)

    def test_basic_response(self):
        """Test basic response for a valid query."""
        assessment2_title = self.assessment2.title
        response = self._get_related_assessments(self.assessment1).json
        self.assertIn("total", response)
        self.assertIn("data", response)
        self.assertEqual(response["total"], 1)
        self.assertEqual(len(response["data"]), 1)
        self.assertEqual(response["data"][0]["title"], assessment2_title)

    @ddt.data(
        ({}, 2),
        ({
            "limit": "0,1"
        }, 2),
        ({
            "limit": "0,2"
        }, 2),
        ({
            "limit": "0,3"
        }, 2),
    )
    @ddt.unpack
    def test_total_count_with_ca(self, limit, expected_count):
        """Test total related assessments count for assessments with ca.

    The left outer join in our eager query on custom attribute values breaks
    the total count if on sa.func.count, but works if we use query.count()
    """
        cad = factories.CustomAttributeDefinitionFactory
        cads = [cad(definition_type="assessment") for _ in range(3)]

        for cad in cads:
            factories.CustomAttributeValueFactory(
                attributable=self.assessment1,
                custom_attribute=cad,
            )
            factories.CustomAttributeValueFactory(
                attributable=self.assessment2,
                custom_attribute=cad,
            )

        with mock.patch("ggrc.views.start_compute_attributes"):
            views.do_reindex()

        response = self._get_related_assessments(self.control, **limit).json
        self.assertEqual(response["total"], expected_count)

    @ddt.data(
        {},
        {"a": 55},
        {
            "object_type": "invalid",
            "object_id": 5
        },
        {
            "object_type": "Control",
            "object_id": "invalid"
        },
        {
            "object_type": "Control",
            "object_id": 5,
            "limit": "a,b"
        },
        {
            "object_type": "Control",
            "object_id": 5,
            "limit": "1"
        },
        {
            "object_type": "Control",
            "object_id": 5,
            "limit": "1,2,5"
        },
        {
            "object_type": "Control",
            "object_id": 5,
            "limit": "5,1"
        },
        {
            "object_type": "Control",
            "object_id": 5,
            "limit": "-5,-1"
        },
        {
            "object_type": "Control",
            "object_id": 5,
            "order_by": "not enough"
        },
    )
    def test_invalid_parameters(self, query_string):
        """Test invalid query parameters {0}."""
        self.assert400(
            self.client.get(self.URL_BASE, query_string=query_string))

    @ddt.data(
        ({}, 2),
        ({
            "limit": "0,1"
        }, 1),
        ({
            "limit": "1,2"
        }, 1),
        ({
            "limit": "1,3"
        }, 1),
        ({
            "limit": "0,2"
        }, 2),
        ({
            "limit": "0,7"
        }, 2),
    )
    @ddt.unpack
    def test_limit_clause(self, limit, expected_count):
        """Test limit clause for {0}."""
        response = self._get_related_assessments(self.control, **limit).json
        self.assertEqual(response["total"], 2)
        self.assertEqual(len(response["data"]), expected_count)

    @ddt.data(
        ({
            "order_by": "title,asc"
        }, ["A_1", "A_2"]),
        ({
            "order_by": "title,desc"
        }, ["A_2", "A_1"]),
        ({
            "order_by": "description,asc,title,asc"
        }, ["A_1", "A_2"]),
        ({
            "order_by": "description,desc,title,desc"
        }, ["A_2", "A_1"]),
    )
    @ddt.unpack
    def test_order_by_clause(self, order_by, titles_order):
        """Test order by for {0}."""
        response = self._get_related_assessments(self.control, **order_by).json
        titles = [assessment["title"] for assessment in response["data"]]
        self.assertEqual(titles, titles_order)

    def test_self_link(self):
        """Test that audits and assessments contain viewLink."""
        audit_self_link = u"/{}/{}".format(
            self.assessment2.audit._inflector.table_plural,
            self.assessment2.audit.id,
        )
        assessment_self_link = u"/{}/{}".format(
            self.assessment2._inflector.table_plural,
            self.assessment2.id,
        )
        response = self._get_related_assessments(self.assessment1).json
        self.assertIn("viewLink", response["data"][0]["audit"])
        self.assertIn("viewLink", response["data"][0])
        self.assertEqual(
            response["data"][0]["audit"]["viewLink"],
            audit_self_link,
        )
        self.assertEqual(
            response["data"][0]["viewLink"],
            assessment_self_link,
        )
