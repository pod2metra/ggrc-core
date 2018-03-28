# coding: utf-8

# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Tests for /query api endpoint."""
# pylint: disable=too-many-arguments
# pylint: disable=too-few-public-methods
import itertools
import re

import sys
from six import add_metaclass
from sqlalchemy import or_, and_

from api_search.base import OPERATIONS, MULTIPLE_ITEMS_COUNT,\
    SingleSetupQueryAPITest, snapshot_mapping, SetupData
from api_search.helpers import create_tuple_data

from ggrc import db
from ggrc.models import inflector
from ggrc.snapshotter.rules import Types


class BaseTestMeta(type):
    """Metaclass for generation tests by parameters provided into Meta:
  model, field, subprops, operators, order, property_case, value_case """

    @classmethod
    def meta_factory(mcs, instance):
        """Factory updating the instance with meta data needed in tests

    Args:
      instance: Created class (result of __new__)
    """
        meta_params = {}
        if hasattr(instance, "Meta"):
            bases = [
                class_ for class_ in reversed(instance.__mro__)
                if issubclass(class_, SingleSetupQueryAPITest)
                and hasattr(class_, "Meta")
            ]
            for base in bases:
                meta_params.update(base.Meta.__dict__.iteritems())
        instance.Meta = type("Meta", (object, ), meta_params)

    def __new__(mcs, name, bases, attrs):
        """Constructor for a new test class instance."""
        instance = super(BaseTestMeta, mcs).__new__(mcs, name, bases, attrs)
        mcs.meta_factory(instance)
        if not hasattr(instance.Meta, "model"):
            return instance
        for params in mcs.vary_params(instance.Meta):
            base_names = [("_filter_by_single_person", True),
                          ("_filter_by_multi_person", False)]
            for base_name, is_single in base_names:
                test_name = mcs._generate_test_name(base_name, params)
                func = mcs._generate_test_filter(instance.Meta, is_single,
                                                 *params)
                func.__name__ = test_name
                setattr(instance, test_name, func)
                setattr(instance, "operator", params[0])
        return instance

    @staticmethod
    def _generate_test_name(base_name, params):
        """Generates unique test case name

    Args:
      base_name: Name for the tests being generated
      params: Params with which the test would be called (to make test
                   name unique)

    Returns:
      String with a test case name
    """
        temp_name = "test{}".format(base_name)
        for param in params:
            if param in OPERATIONS:
                temp_name += "_{}_".format(OPERATIONS[param])
            else:
                temp_name += "_{}_".format(param)

        non_alphanum_re = re.compile(r"\W")
        return re.sub(non_alphanum_re, "", temp_name)

    @staticmethod
    def _generate_test_filter(meta, is_single, operator, order, property_case,
                              value_case):
        """Generate test for query filter

    Args:
      meta: Instance of object with metainformation from child classes
      is_single(bool): If true single case will be tested else multiple
      operator: Operator that should be tested by filter
      order: True - DESC, False - ASC
      property_case: If True, property will be tested in upper case, else lower
      value_case: If True, value will be tested in upper case, else lower

    Returns:
      Test function for provided parameters
    """

        # pylint: disable=protected-access
        # pylint: disable=missing-docstring
        # Comment string is absent to show different test names on every execution
        def test_func(self):
            request_query = []
            test_values = self.get_expected_vals(
                is_single, operator, meta.field, meta.model.__name__)
            for _, value in test_values:
                order_by = {"name": meta.field}
                if order is not None:
                    order_by["desc"] = order

                expression = [
                    meta.field.upper()
                    if property_case else meta.field.lower()
                ]

                if operator != "is empty":
                    expression.append(operator)
                    expression.append(value.upper()
                                      if value_case else value.lower())
                else:
                    expression.append("is")
                    expression.append("empty")

                request_query.append(
                    self._make_query_dict(
                        meta.model.__name__,
                        expression=expression,
                        order_by=[order_by],
                        type_="ids",
                    ))
                if meta.model.__name__ in Types.all:
                    request_query.append(
                        self._make_snapshot_query_dict(
                            meta.model.__name__,
                            expression=expression,
                            order_by=[order_by],
                            type_="ids",
                        ))

            data = self._get_all_result_sets(
                request_query,
                meta.model.__name__,
                "Snapshot",
            )
            BaseTestMeta.assert_result(self, meta, order, is_single, operator,
                                       test_values, data)

        return test_func

    @staticmethod
    def assert_result(instance, meta, order, is_single, operator,
                      expected_values, result_data):
        """Check response of query api for objects and their snapshots"""
        # pylint: disable=too-many-locals
        snapshotable = False
        if meta.model.__name__ in Types.all:
            snapshotable = True

        extra_obj_ids = {}
        if operator in {"!=", "!~", "is empty"}:
            extra_obj_ids = db.session.query(meta.model.id).join(
                SetupData,
                and_(
                    meta.model.id == SetupData.obj_id,
                    meta.model.__name__ == SetupData.model,
                )).filter(
                    and_(
                        or_(
                            SetupData.single != is_single,
                            SetupData.operator != operator,
                            SetupData.field != meta.field,
                        ), SetupData.model == meta.model.__name__))
            # Convert list of tuples to set
            extra_obj_ids = {id_[0] for id_ in extra_obj_ids}

        if snapshotable:
            # Combine objects and their snapshots
            result_pairs = zip(result_data[::2], result_data[1::2])
        else:
            result_pairs = result_data
        for result_pair, expected in zip(result_pairs, expected_values):
            BaseTestMeta.assert_objects(instance, result_pair, expected, meta,
                                        order, extra_obj_ids)
            if snapshotable:
                BaseTestMeta.assert_snapshots(instance, result_pair, expected,
                                              order, extra_obj_ids)

    @staticmethod
    def assert_objects(instance, result, expected, meta, order, extra_ids):
        """Check if received object ids equal to expected"""
        obj_ids = [
            id_ for id_ in result[0][meta.model.__name__]["ids"]
            if id_ not in extra_ids
        ]
        order = order if order else False

        expected_model = expected[0]
        # Sort values by properties if at least one non-empty exist
        if expected[0] and expected[0][0] and expected[0][0].props:
            expected_model = sorted(
                expected[0], key=lambda tup: tup.props.email, reverse=order)
        instance.assertEqual(obj_ids, [exp.id for exp in expected_model])

    @staticmethod
    def assert_snapshots(instance, result, expected, order, extra_ids):
        """Check if received snapshot ids equal to expected"""
        snapshot_ids = result[1]["Snapshot"]["ids"]
        snap_obj_ids = [
            snapshot_mapping[id_] for id_ in snapshot_ids
            if snapshot_mapping[id_] not in extra_ids
        ]
        order = order if order else False

        expected_snap = expected[0]
        # Sort values by properties if at least one non-empty exist
        if expected[0] and expected[0][0] and expected[0][0].props:
            expected_snap = sorted(
                expected[0],
                key=lambda tup: tup.props.user_name,
                reverse=order)
        instance.assertEqual(snap_obj_ids, [exp.id for exp in expected_snap])

    @staticmethod
    def vary_params(meta):
        """Return all combinations of test case input """
        return itertools.product(meta.operators, meta.order,
                                 meta.property_case, meta.value_case)


@add_metaclass(BaseTestMeta)
class BasePersonQueryApiTest(SingleSetupQueryAPITest):
    """Base class for filter tests, containing test cases generation"""

    class Meta(object):
        """Metaclass defining base test parameters"""
        subprops = ["email", "name"]
        operators = OPERATIONS.keys()
        order = [True, False]  # desc = True / asc = False
        property_case = [True, False]  # True ~ upper, False ~ lower
        value_case = [True, False]  # True ~ upper, False ~ lower

    def get_expected_vals(self, single, operator, field, model_name):
        """Collect expected objects for provided combination of test parameters"""
        setup_objs = db.session.query(SetupData).filter(
            and_(
                SetupData.single == single,
                SetupData.operator == operator,
                SetupData.field == field,
                SetupData.model == model_name,
            )).all()
        if not setup_objs:
            return []

        get_exp_func = "expected_{}_{}".format(
            "single" if single else "multiple",
            OPERATIONS[operator],
        )
        return getattr(self, get_exp_func)(setup_objs)

    def expected_single_equal(self, setup_objs):
        """Calculate expected values for single test case, equal operator"""
        values = []
        for data in setup_objs:
            search_obj = inflector.get_model(data.searchable_type).query.get(
                data.searchable_id)
            for subprop in self.Meta.subprops:
                values.append(([
                    create_tuple_data(data.obj_id, search_obj,
                                      self.Meta.subprops)
                ], getattr(search_obj, subprop)))
        return values

    def expected_multiple_equal(self, setup_objs):
        """Calculate expected values for multiple test case, equal operator"""
        values, expected_data = [], []
        search_obj = inflector.get_model(
            setup_objs[0].searchable_type).query.get(
                setup_objs[0].searchable_id)
        for data in setup_objs:
            if data.searchable_id == setup_objs[0].searchable_id:
                expected_data.append(
                    create_tuple_data(data.obj_id, search_obj,
                                      self.Meta.subprops))

        for subprop in self.Meta.subprops:
            values.append((expected_data, getattr(search_obj, subprop)))
        return values

    def expected_single_not_equal(self, setup_objs):
        """Calculate expected values for single test case, not equal operator"""
        values = []
        # Think that data type of all searchable objects is the same
        model = inflector.get_model(setup_objs[0].searchable_type)
        id_searchables = dict(
            db.session.query(model.id, model).filter(
                getattr(model, "id").in_(s.searchable_id for s in setup_objs)))
        for data in setup_objs:
            exp_data = [so for so in setup_objs if so.obj_id != data.obj_id]
            search_obj = id_searchables[data.searchable_id]
            for subprop in self.Meta.subprops:
                values.append(([
                    create_tuple_data(ed.obj_id,
                                      id_searchables[ed.searchable_id],
                                      self.Meta.subprops) for ed in exp_data
                ], getattr(search_obj, subprop)))
        return values

    def expected_multiple_not_equal(self, setup_objs):
        """Calculate expected values for multiple test case, not equal operator"""
        values, expected_data = [], []
        search_obj = inflector.get_model(
            setup_objs[0].searchable_type).query.get(
                setup_objs[0].searchable_id)
        for data in setup_objs:
            if data.searchable_id != setup_objs[0].searchable_id:
                expected_data.append(
                    create_tuple_data(data.obj_id, search_obj,
                                      self.Meta.subprops))
        for subprop in self.Meta.subprops:
            values.append((expected_data, getattr(search_obj, subprop)))
        return values

    def expected_single_contains(self, setup_objs):
        """Calculate expected values for single test case, contains operator"""
        # Expected values are the same as for equal
        return self.expected_single_equal(setup_objs)

    def expected_multiple_contains(self, setup_objs):
        """Calculate expected values for multiple test case, contains operator"""
        # Expected values are the same as for equal
        return self.expected_multiple_equal(setup_objs)

    def expected_single_not_contains(self, setup_objs):
        """Calculate expected values for single test case, not contains operator"""
        # Expected values are the same as for not equal
        return self.expected_single_not_equal(setup_objs)

    def expected_multiple_not_contains(self, setup_objs):
        """Calculate expected values for multiple test case, not contains
    operator"""
        # Expected values are the same as for not equal
        return self.expected_multiple_not_equal(setup_objs)

    def expected_single_is_empty(self, setup_objs):
        """Calculate expected values for single test case, is empty operator"""
        # pylint: disable=no-self-use
        # pylint: disable=unused-argument
        return [([], None)]

    def expected_multiple_is_empty(self, setup_objs):
        """Calculate expected values for multiple test case, is empty operator"""
        # pylint: disable=no-self-use
        expected_data = [
            create_tuple_data(row.obj_id, None, None)
            for row in setup_objs[:MULTIPLE_ITEMS_COUNT]
        ]
        return [(expected_data, None)]


def generate_classes(models, field):
    """Generate test class containing all BasePersonQueryApiTest tests"""

    def generate(model):
        """Create test class with meta information"""
        meta_fields = {"field": field, "model": model}
        meta = type("Meta", (object, ), meta_fields)

        class_name = "Test{}FilterBy{}".format(
            model.__name__.replace(" ", ""), field.replace(" ", "_"))
        instance = type(class_name, (BasePersonQueryApiTest, ), {"Meta": meta})
        return instance

    module = sys.modules[__name__]
    for model in models:
        test_model = generate(inflector.get_model(model))
        setattr(module, test_model.__name__, test_model)
