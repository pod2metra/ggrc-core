# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>


"""Tests for task group task specific export."""

from collections import defaultdict

from ddt import data, ddt

from integration.ggrc_workflows.models import factories
from integration.ggrc.models.factories import PersonFactory
from integration.ggrc import TestCase

from ggrc.models.all_models import CycleTaskGroupObjectTask


@ddt
class TestExportTasks(TestCase):
  """Test imports for basic workflow objects."""

  def setUp(self):
    super(TestExportTasks, self).setUp()
    self.client.get("/login")
    self.headers = {
        'Content-Type': 'application/json',
        "X-Requested-By": "GGRC",
        "X-export-view": "blocks",
    }

  @staticmethod
  def generate_tasks_for_cycle(task_count):
    """generate number of task groups and task for current task group"""
    results = []
    for idx in range(task_count):
      person = PersonFactory(name="user for group {}".format(idx))
      task = factories.CycleTaskFactory(contact=person)
      results.append(task.id)
    return results

  # pylint: disable=invalid-name
  def assertSlugs(self, field, value, slugs):
    """assertion for search cycles for selected fields and values"""
    search_request = [{
        "object_name": "CycleTaskGroupObjectTask",
        "filters": {
            "expression": {
                "left": field,
                "op": {"name": "="},
                "right": value,
            },
        },
        "fields": ["slug"],
    }]
    parsed_data = self.export_parsed_csv(
        search_request
    )["Cycle Task Group Object Task"]
    self.assertEqual(sorted(slugs),
                     sorted([i["Code*"] for i in parsed_data]))
    self.assertEqual(len(slugs), len(parsed_data))

  @data(0, 1, 2)
  def test_filter_by_task_title(self, task_count):
    """Test filter tasks by title"""
    generated = self.generate_tasks_for_cycle(task_count)
    self.assertEqual(bool(task_count), bool(generated))
    for task_id in generated:
      task = CycleTaskGroupObjectTask.query.filter(
          CycleTaskGroupObjectTask.id == task_id
      ).one()
      self.assertSlugs("task title", task.title, [task.slug])

  @data(0, 1, 2)
  def test_filter_by_task_due_date(self, task_count):
    """Test filter by task due date"""
    due_date_dict = defaultdict(set)
    generated = self.generate_tasks_for_cycle(task_count)
    self.assertEqual(bool(task_count), bool(generated))
    for task_id in generated:
      task = CycleTaskGroupObjectTask.query.filter(
          CycleTaskGroupObjectTask.id == task_id
      ).one()
      due_date_dict[str(task.end_date)].add(task.slug)

    for due_date, slugs in due_date_dict.iteritems():
      self.assertSlugs("task due date", due_date, list(slugs))

  @data(0, 1, 2,)
  def test_filter_by_task_assignee(self, task_count):
    """Test filter task by assignee name or email"""
    generated = self.generate_tasks_for_cycle(task_count)
    self.assertEqual(bool(task_count), bool(generated))
    for task_id in generated:
      task = CycleTaskGroupObjectTask.query.filter(
          CycleTaskGroupObjectTask.id == task_id
      ).one()
      self.assertSlugs("task assignee", task.contact.email, [task.slug])
      self.assertSlugs("task assignee", task.contact.name, [task.slug])
