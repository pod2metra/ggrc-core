# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Unit tests for rules generator."""

from unittest import TestCase

import mock

from ggrc.automapper import rules


class TestRules(TestCase):
    """Unit tests for rule set maker."""

    MOCK_TYPE_ORDERING = [["TopLevel"], ["UpperMidLevel1", "UpperMidLevel2"],
                          ["LowerMidLevel1", "LowerMidLevel2"],
                          ["BottomLevel1", "BottomLevel2", "BottomLevel3"]]

    @mock.patch("ggrc.automapper.rules.TYPE_ORDERING", new=MOCK_TYPE_ORDERING)
    def test_explode_rules_ok(self):
        rule1 = rules.Rule({"TopLevel"}, {"UpperMidLevel1", "LowerMidLevel1"},
                           {"BottomLevel1", "BottomLevel3"})
        rule2 = rules.Rule({"TopLevel"}, {"TopLevel"}, {"BottomLevel2"})
        rule3 = rules.Rule({"UpperMidLevel2"}, {"LowerMidLevel1"},
                           {"LowerMidLevel1"})
        rule_list = [rule1, rule2, rule3]

        result = rules.explode_rules(rule_list)

        self.assertEqual(
            sorted(result),
            sorted([
                # rule1 - straight
                ("TopLevel", "UpperMidLevel1", "BottomLevel1"),
                ("TopLevel", "UpperMidLevel1", "BottomLevel3"),
                ("TopLevel", "LowerMidLevel1", "BottomLevel1"),
                ("TopLevel", "LowerMidLevel1", "BottomLevel3"),
                # rule1 - reverse
                ("BottomLevel1", "LowerMidLevel1", "TopLevel"),
                ("BottomLevel3", "LowerMidLevel1", "TopLevel"),
                ("BottomLevel1", "UpperMidLevel1", "TopLevel"),
                ("BottomLevel3", "UpperMidLevel1", "TopLevel"),
                # rule2 - straight
                ("TopLevel", "TopLevel", "BottomLevel2"),
                # rule2 - reverse
                ("BottomLevel2", "TopLevel", "TopLevel"),
                # rule3 - straight
                ("UpperMidLevel2", "LowerMidLevel1", "LowerMidLevel1"),
                # rule3 - reverse
                ("LowerMidLevel1", "LowerMidLevel1", "UpperMidLevel2"),
            ]),
        )

    @mock.patch("ggrc.automapper.rules.TYPE_ORDERING", new=MOCK_TYPE_ORDERING)
    def test_validate_rules_wrong_order(self):
        rule = rules.Rule({"LowerMidLevel1"}, {"TopLevel"}, {"BottomLevel1"})

        with self.assertRaises(rules.AutomappingRuleConfigError):
            rules.validate_rules([rule])

    @mock.patch("ggrc.automapper.rules.TYPE_ORDERING", new=MOCK_TYPE_ORDERING)
    def test_validate_rules_unknown_type(self):
        rule = rules.Rule({"TopLevel"}, {"UnknownType"}, {"BottomLevel1"})

        with self.assertRaises(rules.AutomappingRuleConfigError):
            rules.validate_rules([rule])
