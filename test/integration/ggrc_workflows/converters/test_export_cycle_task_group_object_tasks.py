# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>


"""Tests for task group task specific export."""

from collections import defaultdict

from ddt import data, ddt, unpack

from integration.ggrc_workflows.models import factories
from integration.ggrc.models.factories import PersonFactory
from integration.ggrc import TestCase

from ggrc.models.all_models import CycleTaskGroupObjectTask


@ddt
class TestExportTasks(TestCase):
  """Test imports for basic workflow objects."""

  model = CycleTaskGroupObjectTask

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

  def test_filter_by_task_comment(self):
    """Test filter by comment"""
    task_id = self.generate_tasks_for_cycle(4)[0]
    comment_text = "123"
    task = CycleTaskGroupObjectTask.query.filter(
        CycleTaskGroupObjectTask.id == task_id
    ).one()
    factories.CycleTaskEntryFactory(
        cycle_task_group_object_task=task,
        description=comment_text,
    )
    self.assertSlugs("task comment", comment_text, [task.slug])

  @data(
      ("status", ["Task State", "task state", "task status"]),
      ("end_date", ["Task Due Date", "task due date", "task end_date"]),
      (
          "start_date",
          ["task Start Date", "task start date", "task start_date"],
      ),
  )
  @unpack
  def test_filter_by_aliases(self, field, aliases):
    """Test filter by alias"""
    expected_results = defaultdict(list)
    tasks = CycleTaskGroupObjectTask.query.filter(
        CycleTaskGroupObjectTask.id.in_(self.generate_tasks_for_cycle(4))
    ).all()
    for task in tasks:
      expected_results[str(getattr(task, field))].append(task.slug)
    for value, slugs in expected_results.iteritems():
      for alias in aliases:
        self.assertSlugs(alias, value, slugs)

  @data(
      (
          "updated_at",
          ["task Last updated", "task last updated", "task updated_at"],
      ),
      (
          "created_at",
          ["task Created On", "task created on", "task created_at"],
      ),
  )
  @unpack
  def test_filter_by_datetime_aliases(self, field, aliases):
    """Test filter by datetime field and it's aliases"""
    expected_results = defaultdict(list)
    for task_id in self.generate_tasks_for_cycle(4):
      task = CycleTaskGroupObjectTask.query.get(task_id)
      for value in self.generate_date_strings(getattr(task, field)):
        expected_results[value].append(task.slug)
    for value, slugs in expected_results.iteritems():
      for alias in aliases:
        self.assertSlugs(alias, value, slugs)

  def test_export_by_like_title(self):
    """Test export by like operation"""
    single_name = "absde 123 new foo bar"
    names_pool = [single_name] + single_name.split()
    slugs = {}
    for name in names_pool:
      slugs[name] = factories.CycleTaskFactory(title=name).slug
    for name in names_pool:
      if name == single_name:
        self.assertSlugs("task title", name, slugs.values(), "~")
        self.assertSlugs("task title", name, [], "!~")
      else:
        same_slugs = [slugs[name], slugs[single_name]]
        self.assertSlugs("task title", name, same_slugs, "~")
        self.assertSlugs("task title",
                         name,
                         set(slugs.values()) - set(same_slugs),
                         "!~")
