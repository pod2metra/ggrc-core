# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Integration tests for WithLastComment logic."""

from collections import defaultdict

import collections

from ggrc.models import all_models

from integration.ggrc import TestCase, generator
from integration.ggrc.api_helper import Api
from integration.ggrc.query_helper import WithQueryApi
from integration.ggrc.models import factories


class TestWithLastAssessmentDate(TestCase, WithQueryApi):
    """Integration test suite for WithLastComment functionality."""

    def setUp(self):
        super(TestWithLastAssessmentDate, self).setUp()
        self.client.get("/login")
        self.api = Api()
        self.gen = generator.ObjectGenerator()

        self.asmnt_comments = defaultdict(dict)
        with factories.single_commit():
            for _ in range(3):
                asmnt = factories.AssessmentFactory()
                for _ in range(3):
                    comment = factories.CommentFactory(
                        description=factories.random_str())
                    self.asmnt_comments[asmnt.id][
                        comment.id] = comment.description
                    factories.RelationshipFactory(
                        source=asmnt, destination=comment)

        query = all_models.Revision.query.filter_by(resource_type="Comment")
        revision_ids = [revision.id for revision in query]
        self.api.send_request(
            self.api.client.post,
            api_link="/admin/compute_attributes",
            data={"revision_ids": revision_ids})

    def test_last_comment_value(self):
        """Test assessment has proper value in last_comment field"""
        assessments = all_models.Assessment.query
        self.assertEqual(assessments.count(), len(self.asmnt_comments))
        for asmnt in assessments:
            last_comment_id = max(self.asmnt_comments[asmnt.id])
            self.assertEqual(asmnt.last_comment_id, last_comment_id)
            self.assertEqual(asmnt.last_comment,
                             self.asmnt_comments[asmnt.id][last_comment_id])

    def test_last_comment_filter(self):
        """Test filtration by last comment."""
        asmnt = all_models.Assessment.query.first()
        result = self._get_first_result_set(
            self._make_query_dict(
                "Assessment",
                expression=("Last Comment", "=", asmnt.last_comment),
                type_="ids",
            ),
            "Assessment",
        )
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["ids"], [asmnt.id])

    def test_last_comment_order(self):
        """Test sorting by last comment."""
        result = self._get_first_result_set(
            self._make_query_dict(
                "Assessment", order_by=[{
                    "name": "Last Comment"
                }], type_="ids"),
            "Assessment",
            "ids",
        )
        asmnts = all_models.Assessment.query
        sorted_asmnts = sorted(asmnts, key=lambda k: k.last_comment)
        self.assertEqual(result, [i.id for i in sorted_asmnts])

    def test_export_last_comment(self):
        """Test export Last Assessment Date."""
        search_request = [{
            "object_name": "Assessment",
            "filters": {
                "expression": {},
            },
            "fields": "all",
        }]
        query = self.export_parsed_csv(search_request)["Assessment"]

        exported_comments = [asmnt["Last Comment"] for asmnt in query]
        db_comments = [a.last_comment for a in all_models.Assessment.query]
        self.assertEqual(exported_comments, db_comments)

    def test_import_last_comment(self):
        """Test Last Assessment Date field read only on import."""
        audit = factories.AuditFactory()
        response = self.import_data(
            collections.OrderedDict([
                ("object_type", "Assessment"),
                ("Code*", "Asmnt-code"),
                ("Audit", audit.slug),
                ("Assignees", "user@example.com"),
                ("Creators", "user@example.com"),
                ("Title", "Test title"),
                ("Last Comment", "some comment"),
            ]))
        self._check_csv_response(response, {})
        asmnts = all_models.Assessment.query.filter(
            all_models.Assessment.slug == "Asmnt-code").all()
        self.assertEqual(len(asmnts), 1)
        self.assertEqual(asmnts[0].last_comment, None)

    def test_ca_create_on_import(self):
        """Test creating last_comment CA when comments imported"""
        audit = factories.AuditFactory()
        response = self.import_data(
            collections.OrderedDict([
                ("object_type", "Assessment"),
                ("Code*", "Asmnt-code"),
                ("Audit", audit.slug),
                ("Assignees", "user@example.com"),
                ("Creators", "user@example.com"),
                ("Title", "Test title"),
                ("Comments", "new comment1;;new comment2;;new comment3"),
            ]))
        self._check_csv_response(response, {})
        asmnt = all_models.Assessment.query.filter_by(
            slug="Asmnt-code").first()
        self.assertEqual(asmnt.last_comment, "new comment3")

    def test_ca_update_on_import(self):
        """Test updating of last_comment CA when comments imported"""
        asmnt_id = self.asmnt_comments.keys()[0]
        asmnt_slug = all_models.Assessment.query.get(asmnt_id).slug
        response = self.import_data(
            collections.OrderedDict([
                ("object_type", "Assessment"),
                ("Code*", asmnt_slug),
                ("Comments", "new comment1;;new comment2;;new comment3"),
            ]))
        self._check_csv_response(response, {})
        asmnt = all_models.Assessment.query.filter_by(slug=asmnt_slug).first()
        self.assertEqual(asmnt.last_comment, "new comment3")

    def test_ca_cleanup_on_obj_delete(self):
        """Test cleaning of fulltext and attributes tables on obj delete"""
        asmnt_id = self.asmnt_comments.keys()[0]
        asmnt = all_models.Assessment.query.get(asmnt_id)
        last_comment_records = self.get_model_fulltext(
            "Assessment", "last_comment", [asmnt_id])
        self.assertEqual(last_comment_records.count(), 1)
        last_comment_attrs = self.get_model_ca("Assessment", [asmnt_id])
        self.assertEqual(last_comment_attrs.count(), 1)

        response = self.api.delete(asmnt)
        self.assert200(response)

        last_comment_records = self.get_model_fulltext(
            "Assessment", "last_comment", [asmnt_id])
        self.assertEqual(last_comment_records.count(), 0)
        last_comment_attrs = self.get_model_ca("Assessment", [asmnt_id])
        self.assertEqual(last_comment_attrs.count(), 0)

        # Check that other records weren't affected
        last_comment_records = self.get_model_fulltext(
            "Assessment", "last_comment", self.asmnt_comments.keys())
        self.assertEqual(last_comment_records.count(), 2)
        last_comment_attrs = self.get_model_ca("Assessment",
                                               self.asmnt_comments.keys())
        self.assertEqual(last_comment_attrs.count(), 2)
