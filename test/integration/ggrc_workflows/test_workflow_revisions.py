# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

# pylint: disable=missing-docstring

import unittest

from freezegun import freeze_time
from mock import patch

from ggrc.models import Revision, Event
from ggrc_workflows import start_recurring_cycles
from integration.ggrc_workflows.generator import WorkflowsGenerator
from integration.ggrc.generator import ObjectGenerator
from integration.ggrc import TestCase


class TestRecurringWorkflowRevisions(TestCase):
    """Starting start recurring cycle should generate revisions."""

    def setUp(self):
        super(TestRecurringWorkflowRevisions, self).setUp()
        self.wf_generator = WorkflowsGenerator()
        self.object_generator = ObjectGenerator()

        self.random_objects = self.object_generator.generate_random_objects()
        _, self.person_1 = self.object_generator.generate_person(
            user_role="Administrator")
        _, self.person_2 = self.object_generator.generate_person(
            user_role="Administrator")

        def person_dict(person_id):
            return {
                "href": "/api/people/%d" % person_id,
                "id": person_id,
                "type": "Person"
            }

        self.monthly_workflow = {
            "title":
            "test monthly wf notifications",
            "notify_on_change":
            True,
            "description":
            "some test workflow",
            # admin will be user with id == 1
            "unit":
            "month",
            "repeat_every":
            1,
            "task_groups": [{
                "title":
                "one time task group",
                "contact":
                person_dict(self.person_1.id),
                "task_group_tasks": [{
                    "title": "task 1",
                    "description": "some task",
                    "contact": person_dict(self.person_1.id),
                }, {
                    "title": "task 2",
                    "description": "some task",
                    "contact": person_dict(self.person_1.id),
                }],
                "task_group_objects":
                self.random_objects[:2]
            }, {
                "title":
                "another one time task group",
                "contact":
                person_dict(self.person_1.id),
                "task_group_tasks": [{
                    "title": "task 1 in tg 2",
                    "description": "some task",
                    "contact": person_dict(self.person_1.id),
                }, {
                    "title": "task 2 in tg 2",
                    "description": "some task",
                    "contact": person_dict(self.person_2.id),
                }],
                "task_group_objects": []
            }]
        }

    @unittest.skip("Required to fix log event procedure for new calculator")
    @patch("ggrc.notifications.common.send_email")
    def test_revisions(self, mock_mail):  # pylint: disable=unused-argument
        with freeze_time("2015-04-01"):
            _, workflow = self.wf_generator.generate_workflow(
                self.monthly_workflow)
            self.wf_generator.activate_workflow(workflow)
        event_count = Event.query.count()
        revision_query = Revision.query.filter_by(
            resource_type='CycleTaskGroupObjectTask', )
        revision_count = revision_query.count()
        # cycle starts on monday - 6th, and not on 5th
        with freeze_time("2015-04-03"):
            start_recurring_cycles()

        self.assertEqual(event_count + 1, Event.query.count())
        self.assertNotEqual(revision_count, revision_query.count())
