# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

from ggrc import db
from ggrc_workflows import models
from ggrc_workflows.notification.data_handler import (
    get_cycle_data,
    get_workflow_data,
    get_cycle_task_data,
)
from ggrc_workflows.notification.notification_handler import (
    handle_workflow_modify,
    handle_cycle_task_group_object_task_put,
    handle_cycle_created,
    handle_cycle_modify,
    handle_cycle_task_status_change,
)
from sqlalchemy import event


def empty_notification(*agrs):
  """ Used for ignoring notifications of a certain type """
  return {}


def contributed_notifications():
  """ return handler functions for all object types
  """
  return {
      'Cycle': get_cycle_data,
      'Workflow': get_workflow_data,
      'TaskGroupTask': empty_notification,
      'CycleTaskGroupObjectTask': get_cycle_task_data,
  }


def handle_cycle_task_update(obj):
  handle_cycle_task_group_object_task_put(obj)
  handle_cycle_task_status_change(obj)


def register_listeners():
  new_handlers = {
      models.Cycle: handle_cycle_created,
  }
  delete_handlers = {
  }
  update_handlers = {
      models.Workflow: handle_workflow_modify,
      models.CycleTaskGroupObjectTask: handle_cycle_task_update,
      models.Cycle: handle_cycle_modify,
  }

  @event.listens_for(db.session.__class__, 'after_flush')
  def after_flush_handler(session, flush_context):
    for instance in session.new:
      if instance.__class__ in new_handlers:
        new_handlers[instance.__class__](instance)
    for instance in session.deleted:
      if instance.__class__ in delete_handlers:
        delete_handlers[instance.__class__](instance)
    for instance in session.dirty:
      if instance.__class__ in update_handlers:
        update_handlers[instance.__class__](instance)


"""
All notifications handle the following structure:

  notifications = {
      "some@email.com": {
          "user": { user_info },

          # if notifications are forced for the given workflow
          "force_notifications": {
              notification.id :True/False
          }

          "cycle_starts_in": {
              workflow.id: {
                  "custom_message": ""
                  "title": ""
                  "workflow_url": "",
                  "workflow_owners":
                      { workflow_owner.id: workflow_owner_info, ...},
                  "start_date": MM/DD/YYYY
                  "start_date_statement": "starts in X day[s]" or
                                          "started today|X day[s] ago"
              }
              , ...
          }

          "cycle_start_failed": {
              workflow.id: {
                  "custom_message": ""
                  "title": ""
                  "workflow_url": "",
                  "workflow_owners":
                      { workflow_owner.id: workflow_owner_info, ...},
                  "start_date": MM/DD/YYYY
                  "start_date_statement": "starts in X day[s]" or
                                          "started today|X day[s] ago"
              }
              , ...
          }
          "cycle_data": {
              cycle.id: {
                  "my_tasks" : # list of all tasks assigned to the user
                      { cycle_task.id: { task_info }, ...},
                  # list of all task groups assigned to the user, including
                  # tasks
                  "my_task_groups" :
                      { task_group.id:
                          { cycle_task.id: { task_info }, ... }, ...
                      },
                  "cycle_tasks" : # list of all tasks in the workflow
                      { cycle_task.id: { task_info }, ...}
              }
          }
          "cycle_started": {
              cycle.id: {
                  # manually started cycles have instant notification
                  "manually": False,
                  "custom_message": "",
                  "cycle_title": "",
                  "cycle_url": "",
                  "workflow_owners":
                      { workflow_owner.id: workflow_owner_info, ...}
              }
              , ...
          }

          "task_declined":
              { cycle_task.id: { task_info }, ...}

          "task_reassigned":
              { cycle_task.id: { task_info }, ...}

          "due_in": # tasks due in X days (x depends on notification type)
              { cycle_task.id: { task_info }, ...}

          "due_today":
              { cycle_task.id: { task_info }, ...}

          "all_tasks_completed": # only workflow owner gets this
              { workflow.id: { workflow_info }, ... }
      }
  }


Task and cycle_task have the following structure:

  task = {
      "title": title,
      "object_titles": list of object titles for all related objects
      "end_date": end date in MM/DD/YYYY format
      "due_date_statement": "due today|in X day[s]|X day[s] ago"
      "cycle_task_url" ""
  }

  """
