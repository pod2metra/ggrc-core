# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Ggrc workflow module views."""

from logging import getLogger
from datetime import date

import sqlalchemy as sa

from flask import redirect
from flask import render_template
from flask import url_for

from ggrc import db
from ggrc.models import all_models
from ggrc.app import app
from ggrc.login import login_required
from ggrc.login import get_current_user
from ggrc.utils import benchmark
from ggrc.views.cron import run_job

from ggrc_workflows import start_recurring_cycles
from ggrc_workflows.models import Cycle
from ggrc_workflows.models import CycleTaskGroupObjectTask
from ggrc_workflows.models import Workflow

# pylint: disable=invalid-name
logger = getLogger(__name__)


def get_user_task_count():
    with benchmark("Get user task count RAW"):
        current_user = get_current_user()

        user_tasks = CycleTaskGroupObjectTask.query.with_entities(
            # prefetch tasks' finishing dates to avoid firing subsequent queries
            CycleTaskGroupObjectTask.end_date).join(Cycle).join(
                all_models.AccessControlList,
                sa.and_(
                    all_models.AccessControlList.object_type ==
                    CycleTaskGroupObjectTask.__name__,
                    all_models.AccessControlList.object_id ==
                    CycleTaskGroupObjectTask.id,
                    all_models.AccessControlList.person_id == current_user.id),
            ).join(all_models.AccessControlRole,
                   sa.and_(
                       all_models.AccessControlRole.id ==
                       all_models.AccessControlList.ac_role_id,
                       all_models.AccessControlRole.object_type ==
                       CycleTaskGroupObjectTask.__name__,
                       all_models.AccessControlRole.name.in_(
                           ("Task Assignees", "Task Secondary Assignees")),
                   )).filter(
                       CycleTaskGroupObjectTask.status.in_([
                           CycleTaskGroupObjectTask.ASSIGNED,
                           CycleTaskGroupObjectTask.IN_PROGRESS,
                           CycleTaskGroupObjectTask.FINISHED,
                           CycleTaskGroupObjectTask.DECLINED,
                       ]),
                       Cycle.is_current == True  # noqa # pylint: disable=singleton-comparison
                   ).all()

        task_count = len(user_tasks)

        today = date.today()
        overdue_count = sum(1 for task in user_tasks
                            if task.end_date and today > task.end_date)

        # NOTE: the return value must be a list so that the result can be
        # directly JSON-serialized to an Array in a HAML template
        return [task_count, overdue_count]


@app.context_processor
def workflow_context():
    return {"user_task_count": get_user_task_count}


def _get_unstarted_workflows():
    """Get a list of all workflows that should have a cycle started.

  This function is used for fixing failed cycle starts.

  Returns:
    list of workflows that are missing any started cycles.
  """
    return db.session.query(Workflow).filter(
        Workflow.next_cycle_start_date < date.today(),
        Workflow.recurrences == 1,
        Workflow.status == 'Active',
    ).all()


def unstarted_cycles():
    """View for showing a list of all cycles that are missing.

  Returns:
    html string that displays all missing cycles.
  """
    workflows = _get_unstarted_workflows()
    return render_template("unstarted_cycles.haml", workflows=workflows)


def start_unstarted_cycles():
    """Start missing cycles.

  This function is used for fixing workflow cycles if that  have not been
  automatically started in the nightly cronjob. It should be manually triggered
  by a system administrator.
  """
    workflows = _get_unstarted_workflows()
    for workflow in workflows:
        tasks_start_days = [
            task.relative_start_day for tg in workflow.task_groups
            for task in tg.task_group_tasks
        ]

        tasks_end_days = [
            task.relative_end_day for tg in workflow.task_groups
            for task in tg.task_group_tasks
        ]

        # We must skip tasks that don't have start days and end days defined
        if ((not all(tasks_start_days) and not all(tasks_end_days))
                or (not tasks_start_days and not tasks_end_days)):
            logger.info(
                "Skipping workflow %s (ID: %s) because it doesn't "
                "have relative start and end days specified",
                workflow.title,
                workflow.id,
            )
            continue

        workflow.next_cycle_start_date = date.today()
        workflow.non_adjusted_next_cycle_start_date = date.today()
        db.session.add(workflow)
    db.session.commit()
    run_job(start_recurring_cycles)
    return redirect(url_for('unstarted_cycles'))


def init_extra_views(app_):
    """Init all views neede for ggrc_workflows module.

  Args:
    app: current flask application.
  """
    app_.add_url_rule(
        "/admin/unstarted_cycles", view_func=login_required(unstarted_cycles))

    app_.add_url_rule(
        "/admin/start_unstarted_cycles",
        view_func=login_required(start_unstarted_cycles))
    app_.add_url_rule(
        "/admin/ensure_backlog_workflow_exists",
        view_func=Workflow.ensure_backlog_workflow_exists)
