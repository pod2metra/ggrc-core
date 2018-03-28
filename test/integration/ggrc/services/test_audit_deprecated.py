# coding: utf-8

# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Tests for /query api endpoint."""

import datetime
import operator
from ggrc.models import all_models
from freezegun import freeze_time
from integration.ggrc import TestCase
from integration.ggrc.api_helper import Api
from integration.ggrc.models import factories


class TestAuditDeprecated(TestCase):
    """Test for correct working field last_deprecated_date """

    def setUp(self):
        super(TestAuditDeprecated, self).setUp()
        self.api = Api()

    def test_redefine_status(self):
        """Test create audit and change status to Deprecated"""
        audit = factories.AuditFactory()

        with freeze_time("2017-01-25"):
            self.api.modify_object(audit, {"status": "Deprecated"})

        audit_result = all_models.Audit.query.filter(
            all_models.Audit.id == audit.id).one()

        self.assertEquals(audit_result.last_deprecated_date,
                          datetime.date(2017, 1, 25))

    def test_keep_date_unchanged(self):
        """Test set status audit to Deprecated, and then set status to Planned"""
        audit = factories.AuditFactory()

        with freeze_time("2017-01-25"):
            self.api.modify_object(audit, {"status": "Deprecated"})

        with freeze_time("2017-01-26"):
            self.api.modify_object(audit, {"status": "Planned"})

        audit_result = all_models.Audit.query.filter(
            all_models.Audit.id == audit.id).one()

        self.assertEquals(audit_result.status, "Planned")
        self.assertEquals(audit_result.last_deprecated_date,
                          datetime.date(2017, 1, 25))

    def test_repeat_deprecated_state(self):
        """Test set status audit to Deprecated, then to Planned,
    then to Deprecated and then to Planned"""
        audit = factories.AuditFactory()

        with freeze_time("2017-01-25"):
            self.api.modify_object(audit, {"status": "Deprecated"})

        with freeze_time("2017-01-26"):
            self.api.modify_object(audit, {"status": "Planned"})
        with freeze_time("2017-02-25"):
            self.api.modify_object(audit, {"status": "Deprecated"})
        with freeze_time("2017-02-26"):
            self.api.modify_object(audit, {"status": "Planned"})

        audit_result = all_models.Audit.query.filter(
            all_models.Audit.id == audit.id).one()

        self.assertEquals(audit_result.status, "Planned")
        self.assertEquals(audit_result.last_deprecated_date,
                          datetime.date(2017, 2, 25))

    def test_filter_by_deprecated_date(self):
        """Test filter audits by last deprecated date"""
        amount_of_audits = 5
        list_of_ids = []
        with factories.single_commit():
            with freeze_time("2017-01-25"):
                for _ in range(amount_of_audits):
                    list_of_ids.append(
                        factories.AuditFactory(status="Deprecated").id)

        query_request_data = [{
            "object_name": "Audit",
            'filters': {
                'expression': {
                    'left': 'Last Deprecated Date',
                    'op': {
                        'name': '='
                    },
                    'right': "2017-01-25",
                },
            },
            'type': 'ids',
        }]

        result = self.api.send_request(
            self.api.client.post, data=query_request_data, api_link="/query")
        self.assertItemsEqual(list_of_ids, result.json[0]["Audit"]["ids"])

    def test_sort_by_deprecated_date(self):
        """Test sorting results of filter audits by deprecated date"""
        dict_of_dates = {}
        date_list = ["2017-01-25", "2017-01-29", "2017-01-02", "2017-01-26"]
        with factories.single_commit():
            for date in date_list:
                with freeze_time(date):
                    dict_of_dates[factories.AuditFactory(
                        status="Deprecated").id] = date

        sorted_dict = sorted(dict_of_dates.items(), key=operator.itemgetter(1))
        sorted_list_ids = [item[0] for item in sorted_dict]

        query_request_data = [{
            "object_name": "Audit",
            'filters': {
                'expression': {
                    'left': 'Last Deprecated Date',
                    'op': {
                        'name': '='
                    },
                    'right': "2017-01",
                },
            },
            "order_by": [{
                "name": "last_deprecated_date"
            }],
            'type': 'ids',
        }]

        result = self.api.send_request(
            self.api.client.post, data=query_request_data, api_link="/query")

        self.assertItemsEqual(sorted_list_ids, result.json[0]["Audit"]["ids"])
