# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Integration test for Labeled mixin"""

import collections
import ddt

from integration.ggrc import api_helper
from integration.ggrc.query_helper import WithQueryApi

from integration.ggrc import TestCase
from integration.ggrc.models import factories
from ggrc import db
from ggrc.models import all_models


@ddt.ddt
class TestLabeledMixin(WithQueryApi, TestCase):
    """Test cases for Labeled mixin"""

    def setUp(self):
        super(TestLabeledMixin, self).setUp()
        self.client.get("/login")
        self.api = api_helper.Api()
        self.assessment = factories.AssessmentFactory()

    @staticmethod
    def _get_label_names(response, tag="labels_collection"):
        return [label["name"] for label in response.json[tag]["labels"]]

    @staticmethod
    def _get_labels_dict(names):
        return [{"id": None, "name": name} for name in names]

    @ddt.data(([], []), (["label"], ["label"]),
              (["one", "two", "two "], ["one", "two"]))
    @ddt.unpack
    def test_add_labels(self, names, expected_names):
        """Test labels adding."""
        response = self.api.put(self.assessment,
                                {"labels": self._get_labels_dict(names)})

        self.assert200(response)
        res_names = self._get_label_names(response, "assessment")
        self.assertItemsEqual(res_names, expected_names)

    def test_case_insensitive_labels(self):
        """Test adding labels with names in different case"""
        label = factories.LabelFactory(
            name='Test Label', object_type='Assessment')
        factories.ObjectLabelFactory(
            label=label, labeled_object=self.assessment)
        assessment = factories.AssessmentFactory()
        response = self.api.put(
            assessment, {'labels': self._get_labels_dict(['TEST Label'])})
        self.assert200(response)
        res_names = self._get_label_names(response, 'assessment')
        self.assertEqual(res_names, ['Test Label'])

    def test_labels_update(self):
        """Test labels table updating."""
        response = self.api.put(
            self.assessment, {"labels": self._get_labels_dict(["one", "two"])})
        self.assert200(response)
        response = self.api.put(self.assessment,
                                {"labels": self._get_labels_dict(["three"])})
        self.assert200(response)
        response = self.api.get(all_models.Label, None)
        self.assert200(response)
        names = self._get_label_names(response)
        self.assertItemsEqual(names, ["one", "two", "three"])

    def test_map_label(self):
        """Test labels mapping."""
        # map by id
        label = factories.LabelFactory(
            name=factories.random_str(prefix='label'),
            object_type='Assessment')
        response = self.api.put(self.assessment,
                                {"labels": [{
                                    "id": label.id
                                }]})
        self.assert200(response)
        names = self._get_label_names(response, "assessment")
        self.assertItemsEqual(names, [label.name])

        # map by name
        label = factories.LabelFactory(
            name=factories.random_str(prefix='label'),
            object_type='Assessment')
        response = self.api.put(
            self.assessment, {"labels": self._get_labels_dict([label.name])})
        self.assert200(response)
        names = self._get_label_names(response, "assessment")
        self.assertItemsEqual(names, [label.name])

        # map already mapped label
        response = self.api.put(self.assessment,
                                {"labels": [{
                                    "id": label.id
                                }]})
        self.assert200(response)
        names = self._get_label_names(response, "assessment")
        self.assertItemsEqual(names, [label.name])

        response = self.api.put(
            self.assessment, {"labels": self._get_labels_dict([label.name])})
        self.assert200(response)
        names = self._get_label_names(response, "assessment")
        self.assertItemsEqual(names, [label.name])

    def test_unmap_label(self):
        """Test label deleting"""
        labels = [
            factories.LabelFactory(
                name=factories.random_str(prefix='label'),
                object_type='Assessment') for _ in range(2)
        ]
        for label in labels:
            factories.ObjectLabelFactory(
                labeled_object=self.assessment, label=label)

        response = self.api.put(self.assessment, {'labels': []})
        self.assert200(response)
        labels = response.json['assessment']['labels']
        self.assertEqual(len(labels), 0)

    def test_query_by_empty_label(self):
        """Test exporting Labeled filtered by 'label is empty' """
        query_dict = self._make_query_dict(
            'Assessment', expression=('Label', 'is', 'empty'))
        response = self._get_first_result_set(query_dict, 'Assessment')
        db.session.add(self.assessment)
        self.assertEqual(response['count'], 1)
        self.assertEqual(response['values'][0]['id'], self.assessment.id)

    def test_query_by_label(self):
        """Test query by labels"""
        assessments = [factories.AssessmentFactory() for _ in range(2)]
        assessment_ids = [asmt.id for asmt in assessments]
        label_names = [
            factories.random_str(prefix='label{} '.format(i)) for i in range(2)
        ]
        labels = [
            factories.LabelFactory(name=name, object_type='Assessment')
            for name in label_names
        ]
        factories.ObjectLabelFactory(
            labeled_object=assessments[0], label=labels[0])
        factories.ObjectLabelFactory(
            labeled_object=assessments[0], label=labels[1])
        factories.ObjectLabelFactory(
            labeled_object=assessments[1], label=labels[1])

        query_names = [labels[0].name.lower(), labels[1].name.upper()]

        queries = [
            self._make_query_dict(
                'Assessment', expression=('Label', '=', name))
            for name in query_names
        ]
        by_label = self._get_first_result_set(queries[0], 'Assessment')
        self.assertEqual(by_label['count'], 1)
        self.assertEqual(by_label['values'][0]['id'], assessment_ids[0])

        by_label = self._get_first_result_set(queries[1], 'Assessment')
        self.assertEqual(by_label['count'], 2)
        self.assertSetEqual({asmt['id']
                             for asmt in by_label['values']},
                            set(assessment_ids))

    def test_export_labels(self):
        """Test export of labels"""
        label_name = factories.random_str(prefix='label ')
        label = factories.LabelFactory(
            name=label_name, object_type='Assessment')
        factories.ObjectLabelFactory(
            labeled_object=self.assessment, label=label)

        search_request = [{
            'object_name': 'Assessment',
            'filters': {
                'expression': {}
            },
            'fields': ['labels']
        }]
        query = self.export_parsed_csv(search_request)['Assessment']
        self.assertEqual(query[0]['Labels'], label_name.strip())

    @ddt.data(
        factories.random_str(prefix='label '),
        None,
    )
    def test_export_by_label(self, label_name):
        """Test export assessment by label"""
        if label_name:
            factories.ObjectLabelFactory(
                labeled_object=self.assessment,
                label=factories.LabelFactory(
                    name=label_name, object_type='Assessment'))
            exp = {'left': 'label', 'op': {'name': '='}, 'right': label_name}
        else:
            exp = {'left': 'label', 'op': {'name': 'is'}, 'right': 'empty'}

        data = [{
            'object_name': 'Assessment',
            'fields': 'all',
            'filters': {
                'expression': exp
            }
        }]
        slug = self.assessment.slug
        response = self.export_parsed_csv(data)['Assessment']
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['Code*'], slug)

    def test_import_labels(self):
        """Test import of labels"""
        label_mapped = factories.LabelFactory(
            name=factories.random_str(prefix='label '),
            object_type='Assessment')
        label_unmapped = factories.LabelFactory(
            name=factories.random_str(prefix='label '),
            object_type='Assessment')
        factories.ObjectLabelFactory(
            labeled_object=self.assessment, label=label_mapped)
        response = self.import_data(
            collections.OrderedDict([('object_type', 'Assessment'),
                                     ('Code*', self.assessment.slug),
                                     ('labels', "newbie,{},{}".format(
                                         label_mapped.name,
                                         label_unmapped.name))]))
        self._check_csv_response(response, {})
        labels_count = db.session.query(all_models.Label).count()
        self.assertEqual(labels_count, 3)
        assessment = all_models.Assessment.query.get(self.assessment.id)
        self.assertEqual(len(assessment.labels), 3)

        response = self.import_data(
            collections.OrderedDict([('object_type', 'Assessment'),
                                     ('Code*',
                                      self.assessment.slug), ('labels', "")]))
        self._check_csv_response(response, {})
        labels_count = db.session.query(all_models.Label).count()
        self.assertEqual(labels_count, 3)
        assessment = all_models.Assessment.query.get(self.assessment.id)
        self.assertEqual(len(assessment.labels), 0)

    def test_case_insensitive_import(self):
        """Test import of labels with in different case"""
        label = factories.LabelFactory(
            name="Test Label", object_type='Assessment')
        factories.ObjectLabelFactory(
            labeled_object=self.assessment, label=label)
        response = self.import_data(
            collections.OrderedDict([('object_type', 'Assessment'),
                                     ('Code*', self.assessment.slug),
                                     ('labels', 'TEST Label')]))
        self._check_csv_response(response, {})
        labels_count = db.session.query(all_models.Label).count()
        self.assertEqual(labels_count, 1)

    def test_query_labels(self):
        """Test query labels"""

        assessment_labels = [
            factories.LabelFactory(object_type='Assessment') for _ in range(10)
        ]
        expected_ids = {label.id for label in assessment_labels}
        for _ in range(9):
            factories.LabelFactory(object_type='Control')

        query = self._make_query_dict(
            'Label', expression=('object_type', '=', 'Assessment'))
        labels = self._get_first_result_set(query, 'Label')
        self.assertEqual(labels['count'], 10)
        response_ids = {label['id'] for label in labels['values']}
        self.assertSetEqual(response_ids, expected_ids)
