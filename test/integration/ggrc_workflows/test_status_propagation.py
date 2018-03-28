# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Tests for workflow cycle state propagation between tasks and task groups"""

# pylint: disable=invalid-name
import datetime as dtm

from copy import deepcopy
from threading import Thread
from freezegun import freeze_time

from ggrc import db
from ggrc_workflows.models import Cycle
from ggrc_workflows.models import CycleTaskGroupObjectTask
from ggrc_workflows.models import CycleTaskGroup
from ggrc_workflows.models import Workflow
from integration.ggrc import TestCase
from integration.ggrc_workflows.generator import WorkflowsGenerator
from integration.ggrc.api_helper import Api
from integration.ggrc.generator import ObjectGenerator


class TestWorkflowCycleStatePropagation(TestCase):
    """Test case for cycle task to cycle task group status propagation"""

    def setUp(self):
        super(TestWorkflowCycleStatePropagation, self).setUp()
        self.api = Api()
        self.generator = WorkflowsGenerator()
        self.object_generator = ObjectGenerator()

        self.weekly_wf = {
            "title":
            "weekly thingy",
            "description":
            "start this many a time",
            "unit":
            "week",
            "repeat_every":
            1,
            "task_groups": [
                {
                    "title":
                    "weekly task group",
                    "task_group_tasks": [{
                        "title": "weekly task 1",
                        "start_date": dtm.date(2016, 6, 10),
                        "end_date": dtm.date(2016, 6, 13),
                    }, {
                        "title": "weekly task 1",
                        "start_date": dtm.date(2016, 6, 10),
                        "end_date": dtm.date(2016, 6, 13),
                    }]
                },
            ]
        }

    def test_weekly_state_transitions_assigned_inprogress(self):
        """Test that starting one cycle task changes cycle task group"""

        with freeze_time("2016-6-10 13:00:00"):  # Friday, 6/10/2016
            _, wf = self.generator.generate_workflow(self.weekly_wf)
            self.generator.activate_workflow(wf)

            ctg = db.session.query(CycleTaskGroup).join(Cycle).join(
                Workflow).filter(Workflow.id == wf.id).all()[0]
            self.assertEqual(ctg.status, "Assigned")

            cycle_tasks = db.session.query(CycleTaskGroupObjectTask).join(
                Cycle).join(Workflow).filter(Workflow.id == wf.id).all()
            first_ct, second_ct = cycle_tasks

            for cycle_task in cycle_tasks:
                self.assertEqual(cycle_task.status, "Assigned")

            # Move one task to In Progress
            _, first_ct = self.generator.modify_object(
                first_ct, {"status": "In Progress"})

            self.assertEqual(first_ct.status, "In Progress")
            ctg = db.session.query(CycleTaskGroup).get(ctg.id)
            self.assertEqual(ctg.status, "In Progress")

            # Undo operation
            _, first_ct = self.generator.modify_object(first_ct,
                                                       {"status": "Assigned"})

            self.assertEqual(first_ct.status, "Assigned")
            ctg = db.session.query(CycleTaskGroup).get(ctg.id)
            self.assertEqual(ctg.status, "Assigned")

            # Move both to in progress
            for cycle_task in cycle_tasks:
                self.generator.modify_object(cycle_task,
                                             {"status": "In Progress"})

            ctg = db.session.query(CycleTaskGroup).get(ctg.id)
            self.assertEqual(ctg.status, "In Progress")

            # Undo one cycle task
            _, first_ct = self.generator.modify_object(first_ct,
                                                       {"status": "Assigned"})
            second_ct = db.session.query(CycleTaskGroupObjectTask).get(
                second_ct.id)
            ctg = db.session.query(CycleTaskGroup).get(ctg.id)

            self.assertEqual(first_ct.status, "Assigned")
            self.assertEqual(second_ct.status, "In Progress")
            self.assertEqual(ctg.status, "In Progress")

            # Undo second cycle task
            _, second_ct = self.generator.modify_object(
                second_ct, {"status": "Assigned"})
            first_ct = db.session.query(CycleTaskGroupObjectTask).get(
                first_ct.id)
            ctg = db.session.query(CycleTaskGroup).get(ctg.id)

            self.assertEqual(first_ct.status, "Assigned")
            self.assertEqual(second_ct.status, "Assigned")
            self.assertEqual(ctg.status, "Assigned")

    def test_weekly_state_transitions_inprogress_finished(self):
        """Test In Progress to Finished transitions"""

        with freeze_time("2016-6-10 13:00:00"):  # Friday, 6/10/2016
            _, wf = self.generator.generate_workflow(self.weekly_wf)
            self.generator.activate_workflow(wf)

            ctg = db.session.query(CycleTaskGroup).join(Cycle).join(
                Workflow).filter(Workflow.id == wf.id).all()[0]

            cycle_tasks = db.session.query(CycleTaskGroupObjectTask).join(
                Cycle).join(Workflow).filter(Workflow.id == wf.id).all()
            first_ct, second_ct = cycle_tasks

            # Move both tasks to In Progress
            for cycle_task in cycle_tasks:
                self.generator.modify_object(cycle_task,
                                             {"status": "In Progress"})

            # Test that moving one task to finished doesn't finish entire cycle
            _, first_ct = self.generator.modify_object(first_ct,
                                                       {"status": "Finished"})
            second_ct = db.session.query(CycleTaskGroupObjectTask).get(
                second_ct.id)
            ctg = db.session.query(CycleTaskGroup).get(ctg.id)

            self.assertEqual(first_ct.status, "Finished")
            self.assertEqual(second_ct.status, "In Progress")
            self.assertEqual(ctg.status, "In Progress")

            # Test moving second task to Finished - entire cycle should be finished
            _, second_ct = self.generator.modify_object(
                second_ct, {"status": "Finished"})
            first_ct = db.session.query(CycleTaskGroupObjectTask).get(
                first_ct.id)
            ctg = db.session.query(CycleTaskGroup).get(ctg.id)

            self.assertEqual(second_ct.status, "Finished")
            self.assertEqual(first_ct.status, "Finished")
            self.assertEqual(ctg.status, "Finished")

            # Undo one task, cycle should be In Progress
            _, first_ct = self.generator.modify_object(
                first_ct, {"status": "In Progress"})
            second_ct = db.session.query(CycleTaskGroupObjectTask).get(
                second_ct.id)
            ctg = db.session.query(CycleTaskGroup).get(ctg.id)

            self.assertEqual(first_ct.status, "In Progress")
            self.assertEqual(second_ct.status, "Finished")
            self.assertEqual(ctg.status, "In Progress")

    def test_weekly_state_transitions_finished_verified(self):
        """Test Finished to Verified transitions"""

        with freeze_time("2016-6-10 13:00:00"):  # Friday, 6/10/2016
            _, wf = self.generator.generate_workflow(self.weekly_wf)
            self.generator.activate_workflow(wf)

            ctg = db.session.query(CycleTaskGroup).join(Cycle).join(
                Workflow).filter(Workflow.id == wf.id).all()[0]

            cycle_tasks = db.session.query(CycleTaskGroupObjectTask).join(
                Cycle).join(Workflow).filter(Workflow.id == wf.id).all()
            first_ct, second_ct = cycle_tasks

            # Move both tasks to In Progress
            for cycle_task in cycle_tasks:
                self.generator.modify_object(cycle_task,
                                             {"status": "In Progress"})
                self.generator.modify_object(cycle_task,
                                             {"status": "Finished"})

            ctg = db.session.query(CycleTaskGroup).get(ctg.id)
            self.assertEqual(ctg.status, "Finished")

            for cycle_task in cycle_tasks:
                cycle_task = db.session.query(CycleTaskGroupObjectTask).get(
                    cycle_task.id)
                self.assertEqual(cycle_task.status, "Finished")

            # Verify first CT
            _, first_ct = self.generator.modify_object(first_ct,
                                                       {"status": "Verified"})

            second_ct = db.session.query(CycleTaskGroupObjectTask).get(
                second_ct.id)
            ctg = db.session.query(CycleTaskGroup).get(ctg.id)

            self.assertEqual(first_ct.status, "Verified")
            self.assertEqual(second_ct.status, "Finished")
            self.assertEqual(ctg.status, "Finished")

            # Verify second CT
            _, second_ct = self.generator.modify_object(
                second_ct, {"status": "Verified"})

            first_ct = db.session.query(CycleTaskGroupObjectTask).get(
                first_ct.id)
            ctg = db.session.query(CycleTaskGroup).get(ctg.id)

            self.assertEqual(first_ct.status, "Verified")
            self.assertEqual(second_ct.status, "Verified")
            self.assertEqual(ctg.status, "Verified")

    def test_weekly_state_transitions_finished_declined(self):
        """Test Finished to Declined transitions"""

        with freeze_time("2016-6-10 13:00:00"):  # Friday, 6/10/2016
            _, wf = self.generator.generate_workflow(self.weekly_wf)
            self.generator.activate_workflow(wf)

            ctg = db.session.query(CycleTaskGroup).join(Cycle).join(
                Workflow).filter(Workflow.id == wf.id).all()[0]

            cycle_tasks = db.session.query(CycleTaskGroupObjectTask).join(
                Cycle).join(Workflow).filter(Workflow.id == wf.id).all()
            first_ct, second_ct = cycle_tasks

            # Move both tasks to In Progress
            for cycle_task in cycle_tasks:
                self.generator.modify_object(cycle_task,
                                             {"status": "In Progress"})
                self.generator.modify_object(cycle_task,
                                             {"status": "Finished"})

            ctg = db.session.query(CycleTaskGroup).get(ctg.id)
            self.assertEqual(ctg.status, "Finished")

            # Decline first CT
            _, first_ct = self.generator.modify_object(first_ct,
                                                       {"status": "Declined"})

            second_ct = db.session.query(CycleTaskGroupObjectTask).get(
                second_ct.id)
            ctg = db.session.query(CycleTaskGroup).get(ctg.id)

            self.assertEqual(first_ct.status, "Declined")
            self.assertEqual(second_ct.status, "Finished")
            self.assertEqual(ctg.status, "In Progress")

    def test_deleted_task_state_transitions(self):
        """Test In Progress to Finished transition after task is deleted"""

        with freeze_time("2016-6-10 13:00:00"):  # Friday, 6/10/2016
            _, wf = self.generator.generate_workflow(self.weekly_wf)
            self.generator.activate_workflow(wf)

            ctg = db.session.query(CycleTaskGroup).join(Cycle).join(
                Workflow).filter(Workflow.id == wf.id).all()[0]
            first_ct, second_ct = db.session.query(
                CycleTaskGroupObjectTask).join(Cycle).join(Workflow).filter(
                    Workflow.id == wf.id).all()

            # Move first task to In Progress
            self.generator.modify_object(first_ct, {"status": "In Progress"})
            self.generator.modify_object(first_ct, {"status": "Finished"})
            # Delete second task
            response = self.generator.api.delete(second_ct)
            self.assert200(response)

            ctg = db.session.query(CycleTaskGroup).get(ctg.id)
            self.assertEqual(ctg.status, "Finished")

    def test_cycle_change_on_ct_status_transition(self):
        """Test cycle is_current change on task Finished to In Progress transition
    """
        with freeze_time("2016-6-10 13:00:00"):  # Friday, 6/10/2016
            _, wf = self.generator.generate_workflow(self.weekly_wf)
            self.generator.activate_workflow(wf)

        ctg = db.session.query(CycleTaskGroup).join(Cycle).join(
            Workflow).filter(Workflow.id == wf.id).one()
        c_id = ctg.cycle.id
        first_ct, second_ct = db.session.query(CycleTaskGroupObjectTask).join(
            Cycle).join(Workflow).filter(Workflow.id == wf.id).all()
        self.api.put(first_ct, {"status": "Verified"})
        self.api.put(second_ct, {"status": "Verified"})
        # cycle now should have is_current == False
        cycle = db.session.query(Cycle).get(c_id)

        self.assertEqual(cycle.is_current, False)

        # Move second task back to In Progress
        self.api.put(second_ct, {"status": "In Progress"})
        # cycle now should have is_current == True

        cycle = db.session.query(Cycle).get(ctg.cycle.id)
        self.assertEqual(cycle.is_current, True)

    def test_async_request_state_transitions(self):
        """Test asynchronous transitions"""

        def change_state(cycle_task, status):
            self.generator.api.put(cycle_task, {"status": status})

        updated_wf = deepcopy(self.weekly_wf)
        updated_wf["task_groups"][0]["task_group_tasks"].extend([{
            "title":
            "weekly task 1"
        } for _ in xrange(3)])

        with freeze_time("2016-6-10 13:00:00"):  # Friday, 6/10/2016
            _, wf = self.generator.generate_workflow(updated_wf)
            self.generator.activate_workflow(wf)

            ctg = db.session.query(CycleTaskGroup).join(Cycle).join(
                Workflow).filter(Workflow.id == wf.id).all()[0]

            cycle_tasks = db.session.query(CycleTaskGroupObjectTask).join(
                Cycle).join(Workflow).filter(Workflow.id == wf.id).all()

            # Move all tasks to In Progress
            threads = []
            for cycle_task in cycle_tasks:
                change_state(cycle_task, "In Progress")
                threads.append(
                    Thread(target=change_state, args=(cycle_task, "Finished")))

            for t in threads:
                t.start()
            for t in threads:
                t.join()

            db.session.commit()
            ctg = db.session.query(CycleTaskGroup).get(ctg.id)
            self.assertEqual(ctg.status, "Finished")

    @staticmethod
    def _get_obj(model, title):
        return db.session.query(model).filter(model.title == title).first()

    def test_cycle_task_group_dates(self):
        """Test status and dates when task status is changed """
        wf_data = {
            "title":
            "test workflow",
            "unit":
            "week",
            "repeat_every":
            1,
            "task_groups": [{
                "title":
                "test group",
                "task_group_tasks": [{
                    "title": "task1",
                    "start_date": dtm.date(2016, 6, 10),
                    "end_date": dtm.date(2016, 6, 14),
                }, {
                    "title": "task2",
                    "start_date": dtm.date(2016, 6, 13),
                    "end_date": dtm.date(2016, 6, 15),
                }]
            }]
        }

        with freeze_time("2016-6-10 13:00:00"):  # Friday, 6/10/2016
            _, wf = self.generator.generate_workflow(wf_data)
            self.generator.activate_workflow(wf)

            # check task group status and dates
            tg = self._get_obj(CycleTaskGroup, "test group")
            self.assertEqual(tg.end_date, dtm.date(2016, 6, 15))
            self.assertEqual(tg.next_due_date, dtm.date(2016, 6, 14))
            self.assertEqual(tg.status, "Assigned")

            # move task1 to Verified
            task1 = self._get_obj(CycleTaskGroupObjectTask, "task1")
            self.api.put(task1, {"status": "In Progress"})
            self.api.put(task1, {"status": "Finished"})
            self.api.put(task1, {"status": "Verified"})

            # # check task group status and dates
            tg = self._get_obj(CycleTaskGroup, "test group")
            self.assertEqual(tg.end_date, dtm.date(2016, 6, 15))
            self.assertEqual(tg.next_due_date, dtm.date(2016, 6, 15))
            self.assertEqual(tg.status, "In Progress")

            # move task2 to Verified
            task2 = self._get_obj(CycleTaskGroupObjectTask, "task2")
            self.api.put(task2, {"status": "In Progress"})
            self.api.put(task2, {"status": "Finished"})
            self.api.put(task2, {"status": "Verified"})

            # # check task group status and dates
            tg = self._get_obj(CycleTaskGroup, "test group")
            self.assertIsNone(tg.next_due_date)
            self.assertEqual(tg.status, "Verified")

    def test_empty_group_status(self):
        """Test status and dates when task group is empty """
        wf_data = {
            "title":
            "test workflow",
            "unit":
            "week",
            "repeat_every":
            1,
            "task_groups": [
                {
                    "title":
                    "test group1",
                    "task_group_tasks": [{
                        "title": "task1",
                        "start_date": dtm.date(2016, 6, 10),
                        "end_date": dtm.date(2016, 6, 13),
                    }]
                },
                {
                    # second task group prevents from moving workflow to history
                    "title":
                    "test group2",
                    "task_group_tasks": [{
                        "title": "task2",
                        "start_date": dtm.date(2016, 6, 14),
                        "end_date": dtm.date(2016, 6, 16),
                    }]
                }
            ]
        }

        with freeze_time("2016-6-10 13:00:00"):  # Friday, 6/10/2016
            _, wf = self.generator.generate_workflow(wf_data)
            self.generator.activate_workflow(wf)

            # check task group status and dates
            tg = self._get_obj(CycleTaskGroup, "test group1")
            self.assertEqual(tg.end_date, dtm.date(2016, 6, 13))
            self.assertEqual(tg.next_due_date, dtm.date(2016, 6, 13))
            self.assertEqual(tg.status, "Assigned")

            # move task2 to Verified
            task2 = self._get_obj(CycleTaskGroupObjectTask, "task2")
            self.api.put(task2, {"status": "In Progress"})
            self.api.put(task2, {"status": "Finished"})
            self.api.put(task2, {"status": "Verified"})

            # check task group status
            cycle = self._get_obj(Cycle, "test workflow")
            self.assertEqual(cycle.status, "In Progress")

            # delete task1
            task = self._get_obj(CycleTaskGroupObjectTask, "task1")
            self.api.delete(task)

            # # check task group status and dates
            tg = self._get_obj(CycleTaskGroup, "test group1")
            self.assertIsNone(tg.end_date)
            self.assertIsNone(tg.next_due_date)
            self.assertEqual(tg.status, "Deprecated")

            # # check cycle status
            cycle = self._get_obj(Cycle, "test workflow")
            self.assertEqual(cycle.status, "Verified")
