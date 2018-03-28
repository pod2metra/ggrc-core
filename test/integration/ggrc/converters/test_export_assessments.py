# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Tests for task group task specific export."""
import datetime
from ddt import data, ddt, unpack

from ggrc import db
from ggrc.models import all_models
from integration.ggrc.models import factories
from integration.ggrc import TestCase


@ddt
class TestExport(TestCase):
    """Test imports for assessment objects."""

    model = all_models.Assessment

    def setUp(self):
        super(TestExport, self).setUp()
        self.client.get("/login")
        self.headers = {
            'Content-Type': 'application/json',
            "X-Requested-By": "GGRC",
            "X-export-view": "blocks",
        }
        extr_comment = factories.CommentFactory(description="bad_desc")
        extr_assessment = factories.AssessmentFactory()
        db.engine.execute('update assessments set '
                          'updated_at = "2010-10-10", '
                          'created_at = "2010-10-10";')
        factories.RelationshipFactory(
            source=extr_assessment, destination=extr_comment)
        self.comment = factories.CommentFactory(description="123")
        self.assessment = factories.AssessmentFactory(
            verified_date=datetime.datetime.now(),
            finished_date=datetime.datetime.now(),
        )
        self.rel = factories.RelationshipFactory(
            source=self.comment, destination=self.assessment)

    def test_search_by_comment(self):
        self.assert_slugs("comment", self.comment.description,
                          [self.assessment.slug])

    def test_search_by_new_comment(self):
        """Filter by added new comment and old comment exists"""
        slugs = [self.assessment.slug]
        desc = "321"
        new_comment = factories.CommentFactory(description=desc)
        factories.RelationshipFactory(
            source=new_comment, destination=self.assessment)
        self.assert_slugs("comment", self.comment.description, slugs)
        self.assert_slugs("comment", desc, slugs)

    def test_search_by_deleted_relation(self):
        """Filter by deleted relation to commment"""
        db.session.delete(self.rel)
        db.session.commit()
        self.assert_slugs("comment", self.comment.description, [])

    def test_search_by_deleted_comment(self):
        """Filter by deleted comment"""
        db.session.delete(self.comment)
        db.session.commit()
        self.assert_slugs("comment", self.comment.description, [])

    @data("created_at", "Created Date", "created Date")
    def test_filter_by_created_at(self, alias):
        """Test filter by created at"""
        self.assert_filter_by_datetime(alias, self.assessment.created_at,
                                       [self.assessment.slug])

    @data("updated_at", "Last Updated Date", "Last Updated Date")
    def test_filter_by_updated_at(self, alias):
        """Test filter by updated at"""
        self.assert_filter_by_datetime(alias, self.assessment.updated_at,
                                       [self.assessment.slug])

    @data("finished_date", "Finished Date", "finished date")
    def test_filter_by_finished_date(self, alias):
        """Test filter by finished date"""
        self.assert_filter_by_datetime(alias, self.assessment.finished_date,
                                       [self.assessment.slug])

    @data("verified_date", "Verified Date", "verified date")
    def test_filter_by_verified_date(self, alias):
        """Test filter by verified date"""
        self.assert_filter_by_datetime(alias, self.assessment.verified_date,
                                       [self.assessment.slug])

    def assert_only_date_for(self, alias, operator, date, slugs):
        self.assert_filter_by_datetime(
            alias,
            date,
            slugs,
            formats=["{year}-{month}-{day}"],
            operator=operator)

    def test_filter_not_equal_operators(self):
        """Test filter by != operator."""
        self.assert_only_date_for(
            "verified_date",
            "!=",
            self.assessment.verified_date + datetime.timedelta(1),
            [self.assessment.slug],
        )
        self.assert_only_date_for(
            "verified_date",
            "!=",
            self.assessment.verified_date,
            [],
        )

    def test_filter_not_like_operators(self):
        """Test filter by !~ operator."""
        self.assert_only_date_for(
            "verified_date",
            "!~",
            self.assessment.verified_date + datetime.timedelta(1),
            [self.assessment.slug],
        )
        self.assert_only_date_for(
            "verified_date",
            "!~",
            self.assessment.verified_date,
            [],
        )

    def test_filter_like_operators(self):
        """Test filter by ~ operator."""
        self.assert_only_date_for(
            "verified_date",
            "~",
            self.assessment.verified_date,
            [self.assessment.slug],
        )
        self.assert_only_date_for(
            "verified_date",
            "~",
            self.assessment.verified_date + datetime.timedelta(1),
            [],
        )

    def test_filter_gte_operators(self):
        """Test filter by >= operator."""
        self.assert_only_date_for(
            "verified_date",
            ">=",
            self.assessment.verified_date,
            [self.assessment.slug],
        )
        self.assert_only_date_for(
            "verified_date",
            ">=",
            self.assessment.verified_date + datetime.timedelta(1),
            [],
        )

    def test_filter_gt_operators(self):
        """Test filter by > operator."""
        self.assert_only_date_for(
            "verified_date",
            ">",
            self.assessment.verified_date,
            [],
        )
        self.assert_only_date_for(
            "verified_date",
            ">",
            self.assessment.verified_date - datetime.timedelta(1),
            [self.assessment.slug],
        )

    def test_filter_lte_operators(self):
        """Test filter by <= operator."""
        self.assert_only_date_for(
            "verified_date",
            "<=",
            self.assessment.verified_date,
            [self.assessment.slug],
        )
        self.assert_only_date_for(
            "verified_date",
            "<=",
            self.assessment.verified_date - datetime.timedelta(1),
            [],
        )

    def test_filter_lt_operators(self):
        """Test filter by < operator."""
        self.assert_only_date_for(
            "verified_date",
            "<",
            self.assessment.verified_date,
            [],
        )
        self.assert_only_date_for(
            "verified_date",
            "<",
            self.assessment.verified_date + datetime.timedelta(1),
            [self.assessment.slug],
        )

    @data(
        # (offset, verified_date, filter_date)
        (180, datetime.datetime(2017, 1, 1, 22, 30), "2017-01-02"),
        (-180, datetime.datetime(2017, 1, 2, 1, 30), "2017-01-01"),
        (0, datetime.datetime(2017, 1, 1, 1, 30), "2017-01-01"),
        (None, datetime.datetime(2017, 1, 1, 1, 30), "2017-01-01"),
    )
    @unpack
    def test_filter_by_tz_depend(self, offset, verified_date, filter_value):
        """Test filter by verified date with timezone info"""
        user_headers = {}
        if offset is not None:
            user_headers["X-UserTimezoneOffset"] = str(offset)
        self.assessment.verified_date = verified_date
        db.session.add(self.assessment)
        db.session.commit()
        with self.custom_headers(user_headers):
            self.assert_slugs("verified_date", filter_value,
                              [self.assessment.slug])
