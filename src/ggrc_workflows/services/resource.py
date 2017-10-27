# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Workflow specific Resources implementation."""

import datetime

import sqlalchemy as sa
from flask import current_app
from ggrc import db
from ggrc import utils
from ggrc.services.common import Resource
import ggrc_workflows


class CycleTaskResource(Resource):
  """Contains CycleTask's specific Resource implementation."""

  def patch(self):
    """PATCH operation handler."""
    src = self.request.json
    if self.request.mimetype != 'application/json':
      return current_app.make_response(
          ('Content-Type must be application/json', 415, []))
    with utils.benchmark("Do bulk update"):
      updated_objects = self.model.bulk_update(src)
    updated_ids = set()
    signal_context = []
    workflows = {}
    cycles = {}
    for instance in updated_objects:
      workflows[instance.cycle.workflow_id] = instance.cycle.workflow
      cycles[instance.cycle_id] = instance.cycle
      updated_ids.add(instance.id)
      status_history = sa.inspect(instance).attrs["status"].history
      old_status = status_history.deleted[0]
      new_status = status_history.added[0]
      context_element = ggrc_workflows.Signals.StatusChangeSignalObjectContext(
          instance=instance,
          new_status=new_status,
          old_status=old_status
      )
      signal_context.append(context_element)
    ggrc_workflows.Signals.status_change.send(self.model, objs=signal_context)
    ggrc_workflows.update_cycle_task_object_task_parent_state(
        updated_objects, is_put=True)
    for cycle in cycles.values():
      if cycle.is_current:
        # automaticly moved to hystory cycle if it's status was change to done
        cycle.is_current = cycle.status != cycle.done_status
    for workflow in workflows.values():
      ggrc_workflows.update_workflow_state(workflow)
    with utils.benchmark("Commit"):
      db.session.commit()
    skipped_ids = {int(item['id']) for item in src
                   if int(item["id"]) not in updated_ids}
    with utils.benchmark("Make response"):
      result = [{'status': 'updated', 'id': idx} for idx in updated_ids]
      result.extend([{'status': 'skipped', 'id': idx} for idx in skipped_ids])
      return self.json_success_response(result, datetime.datetime.now())
