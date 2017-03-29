# coding: utf-8

# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Tests for /query api endpoint."""

from sqlalchemy import func
from flask import json

from ddt import ddt
from ddt import data

from ggrc import app
from ggrc import views
from ggrc import models
from ggrc import db

from integration.ggrc import TestCase
from integration.ggrc import generator
from integration.ggrc.models import factories
from integration.ggrc.services.test_query.test_basic import (
    BaseQueryAPITestCase)


# pylint: disable=super-on-old-class
@ddt
class TestAuditSnapshotQueries(TestCase):
  """Tests for /query api for Audit snapshots"""

  # objects mapped to assessments after set up:
  # Assessment 1 -- Market 1,
  # Assessment 2 -- Market 2, Control 1,
  # Assessment 3 -- Market 3, Control 1, Control 2
  # Assessment 4 -- Market 4, Control 1, Control 2, Control 3

  # Number of controls mapped to assessments
  ASSESSMENT_COUNTS = {
      "Assessment 1": 0,
      "Assessment 2": 1,
      "Assessment 3": 2,
      "Assessment 4": 3,
  }

  # Number of assessments mapped to controls
  CONTROL_COUNTS = {
      "Control 0": 0,  # unmapped control
      "Control 1": 3,
      "Control 2": 2,
      "Control 3": 1,
      "Control 4": 0,
      "Control 5": 0,
  }

  AUDIT_COUNTS = {
      "Control 0": 0,  # unmapped control
      "Control 1": 1,
      "Control 2": 1,
  }

  def setUp(self):
    """Log in before performing queries."""
    self.client.get("/login")

  def _post(self, request_data):
    return self.client.post(
        "/query",
        data=json.dumps(request_data),
        headers={"Content-Type": "application/json", }
    )

  @classmethod
  def setUpClass(cls):
    TestCase.clear_data()
    with app.app.app_context():
      cls._setup_objects()

  @staticmethod
  def _create_users():
    """Create users needed for testing."""
    users = [
        "user1@example.com",
        "user2@example.com",
        "user3@example.com",
        "user4@example.com",
        "user5@example.com"
    ]
    for user in users:
      factories.PersonFactory(email=user)

  @staticmethod
  def _create_snapshotable_objects():
    """Create original objects that will be snapshotted."""
    text_cad = factories.CustomAttributeDefinitionFactory(
        title="text cad",
        definition_type="market",
    )
    date_cad = factories.CustomAttributeDefinitionFactory(
        title="date cad",
        definition_type="market",
        attribute_type="Date",
    )
    person_cad = factories.CustomAttributeDefinitionFactory(
        title="CA person",
        definition_type="market",
        attribute_type="Map:Person",
    )

    for i in range(5):
      factories.ControlFactory(title="Control {}".format(i + 1))
      factories.OrgGroupFactory()
      market = factories.MarketFactory(title="Market {}".format(i + 1))
      factories.CustomAttributeValueFactory(
          custom_attribute=date_cad,
          attributable=market,
          attribute_value="2016-11-0{}".format(i + 3),
      )
      factories.CustomAttributeValueFactory(
          custom_attribute=text_cad,
          attributable=market,
          attribute_value="2016-11-0{}".format(i + 1),
      )
      factories.CustomAttributeValueFactory(
          custom_attribute=person_cad,
          attributable=market,
          attribute_value="user{}@example.com".format(i + 1),
      )

  @classmethod
  def _setup_objects(cls):
    """Create and reindex objects needed for tests"""
    cls._create_users()
    cls._create_snapshotable_objects()

    revisions = models.Revision.query.filter(
        models.Revision.resource_type.in_(["OrgGroup", "Market", "Control"]),
        models.Revision.id.in_(
            db.session.query(func.max(models.Revision.id)).group_by(
                models.Revision.resource_type,
                models.Revision.resource_id,
            )
        ),
    )

    audit = factories.AuditFactory()

    snapshots = [
        factories.SnapshotFactory(
            child_id=revision.resource_id,
            child_type=revision.resource_type,
            revision=revision,
            parent=audit,
        )
        for revision in revisions
    ]

    snapshot_map = {snapshot.revision.content["title"]: snapshot
                    for snapshot in snapshots}

    # create Assessments and issues and map some snapshots to them
    # Markets and Controls represent snapshots of those objects.

    assessment_issues = (
        factories.AssessmentFactory,
        factories.IssueFactory,
    )
    for i in range(4):
      for factory in assessment_issues:
        # pylint: disable=protected-access
        obj = factory(
            title="{} {}".format(factory._meta.model.__name__, i + 1),
            audit=audit,
        )
        factories.RelationshipFactory(
            source=audit if i % 2 == 0 else obj,
            destination=audit if i % 2 == 1 else obj,
        )

        market = snapshot_map["Market {}".format(i + 1)]
        factories.RelationshipFactory(
            source=market if i % 2 == 0 else obj,
            destination=market if i % 2 == 1 else obj,
        )
        for j in range(i):
          control = snapshot_map["Control {}".format(j + 1)]
          factories.RelationshipFactory(
              source=control if i % 2 == 0 else obj,
              destination=control if i % 2 == 1 else obj,
          )

    # Create an unmapped control for base tests
    factories.ControlFactory(title="Control 0")

    views.do_reindex()

  def test_basic_snapshot_query(self):
    """Test fetching all snapshots for a given Audit."""
    result = self._post([
        {
            "object_name": "Snapshot",
            "filters": {
                "expression": self._get_model_expression(),
                "keys": [],
                "order_by": {"keys": [], "order": "", "compare": None}
            }
        }
    ])
    self.assertEqual(len(result.json[0]["Snapshot"]["values"]), 5)

    result = self._post([
        {
            "object_name": "Snapshot",
            "filters": {
                "expression": self._get_model_expression("OrgGroup"),
                "keys": [],
                "order_by": {"keys": [], "order": "", "compare": None}
            }
        }
    ])
    self.assertEqual(len(result.json[0]["Snapshot"]["values"]), 5)

  def test_snapshot_attribute_filter(self):
    """Test filtering snapshots on object attributes."""
    market_title = models.Market.query.first().title
    result = self._post([
        {
            "object_name": "Snapshot",
            "filters": {
                "expression": {
                    "left": self._get_model_expression(),
                    "op": {"name": "AND"},
                    "right": {
                        "left": "title",
                        "op": {"name": "="},
                        "right": market_title,
                    },
                },
                "keys": [],
                "order_by": {"keys": [], "order": "", "compare": None}
            }
        }
    ])
    self.assertEqual(len(result.json[0]["Snapshot"]["values"]), 1)
    content = result.json[0]["Snapshot"]["values"][0]["revision"]["content"]
    self.assertEqual(
        content["title"],
        market_title,
    )

    result = self._post([
        {
            "object_name": "Snapshot",
            "filters": {
                "expression": {
                    "left": self._get_model_expression("OrgGroup"),
                    "op": {"name": "AND"},
                    "right": {
                        "left": "title",
                        "op": {"name": "!="},
                        "right": models.OrgGroup.query.first().title,
                    },
                },
                "keys": [],
                "order_by": {"keys": [], "order": "", "compare": None}
            }
        }
    ])
    self.assertEqual(len(result.json[0]["Snapshot"]["values"]), 4)

  def test_snapshot_date_ca_filter(self):
    """Test filtering snapshots by date custom attributes."""
    result = self._post([
        {
            "object_name": "Snapshot",
            "filters": {
                "expression": {
                    "left": self._get_model_expression(),
                    "op": {"name": "AND"},
                    "right": {
                        "left": {
                            "left": "text cad",
                            "op": {"name": "="},
                            "right": "2016-11-01",  # one match
                        },
                        "op": {"name": "OR"},
                        "right": {
                            "left": "date cad",
                            "op": {"name": ">"},
                            "right": "11/05/2016",  # 2 matches
                        },
                    },
                },
                "keys": [],
                "order_by": {"keys": [], "order": "", "compare": None}
            }
        }
    ])
    self.assertEqual(len(result.json[0]["Snapshot"]["values"]), 3)

  def test_snapshot_person_ca_filter(self):
    """Test filtering snapshots by person custom attribute."""
    result = self._post([
        {
            "object_name": "Snapshot",
            "filters": {
                "expression": {
                    "left": self._get_model_expression(),
                    "op": {"name": "AND"},
                    "right": {
                        "left": {
                            "left": "text cad",
                            "op": {"name": "="},
                            "right": "2016-11-01",  # 1 match
                        },
                        "op": {"name": "OR"},
                        "right": {
                            "left": "CA person",
                            "op": {"name": "="},
                            "right": "user2@example.com",  # 1 match
                        },
                    },
                },
                "keys": [],
                "order_by": {"keys": [], "order": "", "compare": None}
            }
        }
    ])
    self.assertEqual(len(result.json[0]["Snapshot"]["values"]), 2)

  @data(*CONTROL_COUNTS.items())
  def test_assesessment_relationships(self, test_data):
    """Test relationships between Assessments and original objects."""
    title, expected = test_data
    control = models.Control.query.filter_by(title=title).first()

    result = self._post([
        {
            "object_name": "Assessment",
            "filters": {
                "expression": {
                    "object_name": "Control",
                    "op": {"name": "relevant"},
                    "ids": [control.id]
                },
                "keys": [],
                "order_by": {"keys": [], "order": "", "compare": None}
            }
        }
    ])
    count = len(result.json[0]["Assessment"]["values"])
    self.assertEqual(count, expected,
                     "Invalid related Assessment count for '{}'."
                     "Expected {}, got {}".format(title, expected, count))

  @data(*ASSESSMENT_COUNTS.items())
  def test_original_objects(self, test_data):
    """Test relationships between original objects and Assessments."""
    title, expected = test_data
    assessment = models.Assessment.query.filter_by(title=title).first()

    result = self._post([
        {
            "object_name": "Control",
            "filters": {
                "expression": {
                    "object_name": "Assessment",
                    "op": {"name": "relevant"},
                    "ids": [assessment.id]
                },
                "keys": [],
                "order_by": {"keys": [], "order": "", "compare": None}
            }
        }
    ])
    count = len(result.json[0]["Control"]["values"])
    self.assertEqual(count, expected,
                     "Invalid related Control count for '{}'."
                     "Expected {}, got {}".format(title, expected, count))

  def test_audit_empty_queries(self):
    """Test Audit relationship for irrelevant objects."""
    result = self._post([
        {
            "object_name": "Audit",
            "filters": {
                "expression": {
                    "object_name": "Control",
                    "op": {"name": "relevant"},
                    "ids": [-1]
                },
                "keys": [],
                "order_by": {"keys": [], "order": "", "compare": None}
            }
        }
    ])
    count = len(result.json[0]["Audit"]["values"])
    expected = 0
    self.assertEqual(count, expected,
                     "Invalid related Audit count for Audit."
                     "Expected {}, got {}".format(expected, count))

  def test_audit_parent_relationships(self):
    """Test snapshotted object relationship to Audits."""
    audit = models.Audit.query.first()
    result = self._post([
        {
            "object_name": "Control",
            "filters": {
                "expression": {
                    "object_name": "Audit",
                    "op": {"name": "relevant"},
                    "ids": [audit.id]
                },
                "keys": [],
                "order_by": {"keys": [], "order": "", "compare": None}
            }
        }
    ])
    count = len(result.json[0]["Control"]["values"])
    expected = 5  # Audit should contain 5 control snapshots
    self.assertEqual(count, expected,
                     "Invalid related Control count for Audit."
                     "Expected {}, got {}".format(expected, count))

  @data(*AUDIT_COUNTS.items())
  def test_audit_child_relationships(self, test_data):
    """Test audit relationships for snapshotted objects."""
    title, expected = test_data
    control = models.Control.query.filter_by(title=title).first()

    result = self._post([
        {
            "object_name": "Audit",
            "filters": {
                "expression": {
                    "object_name": "Control",
                    "op": {"name": "relevant"},
                    "ids": [control.id]
                },
                "keys": [],
                "order_by": {"keys": [], "order": "", "compare": None}
            }
        }
    ])
    count = len(result.json[0]["Audit"]["values"])
    self.assertEqual(count, expected,
                     "Invalid related Audit count for '{}'."
                     "Expected {}, got {}".format(title, expected, count))

  @staticmethod
  def _get_model_expression(model_name="Market"):
    return {
        "left": {
            "left": "child_type",
            "op": {"name": "="},
            "right": model_name,
        },
        "op": {"name": "AND"},
        "right": {
            "object_name": "Audit",
            "op": {"name": "relevant"},
            "ids": [models.Audit.query.first().id]
        }
    }


class TestSnapshotIndexing(BaseQueryAPITestCase):
  """Test suite to check indexing of special fields in Snapshots."""

  def setUp(self):
    super(TestSnapshotIndexing, self).setUp()
    self.generator = generator.ObjectGenerator()

  @classmethod
  def _make_snapshot_query_dict(cls, child_type, expression=None, *args,
                                **kwargs):
    """Make a dict with query for Snapshots of child_type."""
    child_type_filter = cls.make_filter_expression(("child_type", "=",
                                                    child_type))
    if expression:
      snapshot_filter = cls.make_filter_expression(expression)
      filters = {"expression": {"op": {"name": "AND"},
                                "left": snapshot_filter,
                                "right": child_type_filter}}
    else:
      filters = {"expression": child_type_filter}

    return cls._make_query_dict_base("Snapshot", filters=filters, *args,
                                     **kwargs)

  def test_process_network_zone(self):
    """Process Snapshots are filtered and sorted by "network zone"."""
    program = factories.ProgramFactory()
    nz_core = db.session.query(models.Option).filter_by(title="Core").one()
    nz_prod = db.session.query(models.Option).filter_by(title="Prod").one()
    process_nz_core = factories.ProcessFactory(network_zone=nz_core)
    process_nz_prod = factories.ProcessFactory(network_zone=nz_prod)
    factories.RelationshipFactory(source=program, destination=process_nz_core)
    factories.RelationshipFactory(source=program, destination=process_nz_prod)
    process_nz_core_id = process_nz_core.id
    process_nz_prod_id = process_nz_prod.id

    # AuditFactory doesn't trigger Snapshotter
    self.generator.generate_object(models.Audit, {
        "title": "test_process_network_zone",
        "program": {"id": program.id},
        "status": "Planned",
        "snapshots": {
            "operation": "create",
        }
    })

    process_nz_core_result = self._get_first_result_set(
        self._make_snapshot_query_dict("Process",
                                       expression=["Network Zone", "=",
                                                   "Core"]),
        "Snapshot",
    )
    self.assertEqual(process_nz_core_result["count"], 1)
    self.assertTrue(all(snap["revision"]["content"]["network_zone"]
                        ["title"] == "Core"
                        for snap in process_nz_core_result["values"]))
    process_nz_prod_result = self._get_first_result_set(
        self._make_snapshot_query_dict("Process",
                                       expression=["Network Zone", "=",
                                                   "prod"]),
        "Snapshot",
    )
    self.assertEqual(process_nz_prod_result["count"], 1)
    self.assertTrue(all(snap["revision"]["content"]["network_zone"]
                        ["title"] == "Prod"
                        for snap in process_nz_prod_result["values"]))

    order_by_nz_result = self._get_first_result_set(
        self._make_snapshot_query_dict("Process",
                                       order_by=[{"name": "Network Zone"}]),
        "Snapshot",
    )
    self.assertEqual(order_by_nz_result["count"], 2)
    self.assertListEqual([snap["child_id"]
                          for snap in order_by_nz_result["values"]],
                         [process_nz_core_id, process_nz_prod_id])
