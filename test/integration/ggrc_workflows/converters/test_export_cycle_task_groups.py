# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>


"""Tests for task group task specific export."""

from collections import defaultdict

from ddt import data, unpack, ddt

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
  def generate_tasks_for_cycle(group_count, task_count):
    """generate number of task groups and task for current task group"""
    results = {}
    workflow = factories.WorkflowFactory()
    cycle = factories.CycleFactory(workflow=workflow)
    task_group = factories.TaskGroupFactory(workflow=workflow)
    for idx in range(group_count):
      person = PersonFactory(name="user for group {}".format(idx))
      cycle_task_group = factories.CycleTaskGroupFactory(cycle=cycle,
                                                         contact=person)
      for _ in range(task_count):
        task_group_task = factories.TaskGroupTaskFactory(
            task_group=task_group, contact=person)
        task = factories.CycleTaskFactory(cycle=cycle,
                                          cycle_task_group=cycle_task_group,
                                          contact=person,
                                          task_group_task=task_group_task)
        results[task.id] = cycle_task_group.slug
    return results

  # pylint: disable=invalid-name
  def assertSlugs(self, field, value, slugs):
    """assertion for search cycles for selected fields and values"""
    search_request = [{
        "object_name": "CycleTaskGroup",
        "filters": {
            "expression": {
                "left": field,
                "op": {"name": "="},
                "right": value,
            },
        },
        "fields": ["slug"],
    }]
    parsed_data = self.export_parsed_csv(search_request)["Cycle Task Group"]
    self.assertEqual(sorted(slugs),
                     sorted([i["Code*"] for i in parsed_data]))
    self.assertEqual(len(slugs), len(parsed_data))

  @data(
      #  (Cycle count, tasks in cycle)
      (0, 0),
      (1, 1),
      (2, 1),
      (2, 1),
      (2, 2),
  )
  @unpack
  def test_filter_by_task_title(self, group_count, task_count):
    """Test filter groups by task title"""
    generated = self.generate_tasks_for_cycle(group_count, task_count)
    self.assertEqual(bool(group_count), bool(generated))
    for task_id, slug in generated.iteritems():
      task = CycleTaskGroupObjectTask.query.filter(
          CycleTaskGroupObjectTask.id == task_id
      ).one()
      self.assertSlugs("task title", task.title, [slug])

  @data(
      #  (Cycle count, tasks in cycle)
      (0, 0),
      (1, 1),
      (2, 1),
      (2, 1),
      (2, 2),
  )
  @unpack
  def test_filter_group_title(self, group_count, task_count):
    """Test filter groups by title"""
    generated = self.generate_tasks_for_cycle(group_count, task_count)
    self.assertEqual(bool(group_count), bool(generated))
    for task_id, slug in generated.iteritems():
      task = CycleTaskGroupObjectTask.query.filter(
          CycleTaskGroupObjectTask.id == task_id
      ).one()
      self.assertSlugs("group title", task.cycle_task_group.title, [slug])

  @data(
      #  (Cycle count, tasks in cycle)
      (0, 0),
      (1, 1),
      (2, 1),
      (2, 1),
      (2, 2),
  )
  @unpack
  def test_filter_by_task_due_date(self, group_count, task_count):
    """Test filter by task due date"""
    due_date_dict = defaultdict(set)
    generated = self.generate_tasks_for_cycle(group_count, task_count)
    self.assertEqual(bool(group_count), bool(generated))
    for task_id, slug in generated.iteritems():
      task = CycleTaskGroupObjectTask.query.filter(
          CycleTaskGroupObjectTask.id == task_id
      ).one()
      due_date_dict[str(task.end_date)].add(slug)

    for due_date, slugs in due_date_dict.iteritems():
      self.assertSlugs("task due date", due_date, list(slugs))

  @data(
      #  (Cycle count, tasks in cycle)
      (0, 0),
      (1, 1),
      (2, 1),
      (2, 1),
      (2, 2),
  )
  @unpack
  def test_filter_by_group_due_date(self, group_count, task_count):
    """Test filter by group due date"""
    due_date_dict = defaultdict(set)
    generated = self.generate_tasks_for_cycle(group_count, task_count)
    self.assertEqual(bool(group_count), bool(generated))
    for task_id, slug in generated.iteritems():
      task = CycleTaskGroupObjectTask.query.filter(
          CycleTaskGroupObjectTask.id == task_id
      ).one()
      due_date_dict[str(task.cycle_task_group.next_due_date)].add(slug)

    for due_date, slugs in due_date_dict.iteritems():
      self.assertSlugs("group due date", due_date, list(slugs))

  @data(
      #  (Cycle count, tasks in cycle)
      (0, 0),
      (1, 1),
      (2, 1),
      (2, 1),
      (2, 2),
  )
  @unpack
  def test_filter_by_group_assignee(self, group_count, task_count):
    """Test filter by group assignee name or email"""
    generated = self.generate_tasks_for_cycle(group_count, task_count)
    self.assertEqual(bool(group_count), bool(generated))
    for task_id, slug in generated.iteritems():
      task = CycleTaskGroupObjectTask.query.filter(
          CycleTaskGroupObjectTask.id == task_id
      ).one()
      self.assertSlugs(
          "group assignee", task.cycle_task_group.contact.email, [slug])
      self.assertSlugs(
          "group assignee", task.cycle_task_group.contact.name, [slug])

  @data(
      #  (Cycle count, tasks in cycle)
      (0, 0),
      (1, 1),
      (2, 1),
      (2, 1),
      (2, 2),
  )
  @unpack
  def test_filter_by_task_assignee(self, group_count, task_count):
    """Test filter cycles by task assignee name or email"""
    generated = self.generate_tasks_for_cycle(group_count, task_count)
    self.assertEqual(bool(group_count), bool(generated))
    for task_id, slug in generated.iteritems():
      task = CycleTaskGroupObjectTask.query.filter(
          CycleTaskGroupObjectTask.id == task_id
      ).one()
      self.assertSlugs("task assignee", task.contact.email, [slug])
      self.assertSlugs("task assignee", task.contact.name, [slug])
