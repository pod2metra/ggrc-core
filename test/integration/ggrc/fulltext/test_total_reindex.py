# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Test for total reindex procedure"""

from ggrc import fulltext

from ggrc import views
from integration.ggrc import TestCase
from integration.ggrc.models import factories as ggrc_factories
from integration.ggrc_workflows.models import factories as wf_factories


class TestTotalTeindex(TestCase):
  """Tests for total reindex procedure."""

  def setUp(self):
    views.do_reindex()

  INDEXED_MODEL_FACTORIES = [
      ggrc_factories.AuditFactory,
      ggrc_factories.AssessmentFactory,
      ggrc_factories.AssessmentTemplateFactory,
      ggrc_factories.CommentFactory,
      ggrc_factories.ContractFactory,
      ggrc_factories.ControlFactory,
      ggrc_factories.IssueFactory,
      ggrc_factories.MarketFactory,
      ggrc_factories.ObjectiveFactory,
      ggrc_factories.OrgGroupFactory,
      ggrc_factories.PersonFactory,
      ggrc_factories.PolicyFactory,
      ggrc_factories.ProcessFactory,
      ggrc_factories.ProgramFactory,
      ggrc_factories.RegulationFactory,
      wf_factories.CycleFactory,
      wf_factories.CycleTaskGroupFactory,
      wf_factories.CycleTaskEntryFactory,
      wf_factories.CycleTaskFactory,
      wf_factories.TaskGroupFactory,
      wf_factories.TaskGroupObjectFactory,
      wf_factories.TaskGroupTaskFactory,
      wf_factories.WorkflowFactory,
  ]

  def test_simple_reindex(self):
    """Test for check simple reindex procedure."""
    with ggrc_factories.single_commit():
      for factory in self.INDEXED_MODEL_FACTORIES:
        for _ in range(5):
          factory()
    indexer = fulltext.get_indexer()
    count = indexer.record_type.query.count()
    views.do_reindex()
    self.assertEqual(count, indexer.record_type.query.count())
