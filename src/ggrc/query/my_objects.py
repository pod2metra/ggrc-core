# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""This module helper query builder for my dashboard page."""
import sqlalchemy as sa
from sqlalchemy import and_
from sqlalchemy import literal
from sqlalchemy import true, false
from sqlalchemy import union
from sqlalchemy import alias
from ggrc import db
from ggrc.models import all_models
from ggrc.models.custom_attribute_value import CustomAttributeValue
from ggrc_basic_permissions import backlog_workflows
from ggrc_workflows.models import Cycle


def _types_to_type_models(types):
    """Convert string types to real objects."""
    if types is None:
        return all_models.all_models
    return [m for m in all_models.all_models if m.__name__ in types]


def _get_people():
    """Get all the people w/o any restrictions."""
    all_people = db.session.query(
        all_models.Person.id.label('id'),
        literal(all_models.Person.__name__).label('type'),
        literal(None).label('context_id'))
    return all_people


def _get_object_mapped_ca(contact_id, model_names):
    """Objects to which the user is mapped via a custom attribute."""
    ca_mapped_objects_query = db.session.query(
        CustomAttributeValue.attributable_id.label('id'),
        CustomAttributeValue.attributable_type.label('type'),
        literal(None).label('context_id')).filter(
            and_(CustomAttributeValue.attribute_value == "Person",
                 CustomAttributeValue.attribute_object_id == contact_id,
                 CustomAttributeValue.attributable_type.in_(model_names)))
    return ca_mapped_objects_query


def _get_custom_roles(contact_id, model_names):
    """Objects for which the user is an 'owner'."""
    custom_roles_query = db.session.query(
        all_models.AccessControlList.object_id.label('id'),
        all_models.AccessControlList.object_type.label('type'),
        literal(None).label('context_id')).join(
            all_models.AccessControlRole,
            all_models.AccessControlList.ac_role_id ==
            all_models.AccessControlRole.id).filter(
                and_(all_models.AccessControlList.person_id == contact_id,
                     all_models.AccessControlList.object_type.in_(model_names),
                     all_models.AccessControlRole.my_work == true(),
                     all_models.AccessControlRole.read == true()))
    return custom_roles_query


def get_myobjects_query(types=None, contact_id=None):  # noqa
    """Filters by "myview" for a given person.

  Finds all objects which might appear on a user's Profile or Dashboard
  pages.

  This method only *limits* the result set -- Contexts and Roles will still
  filter out forbidden objects.
  """
    type_models = _types_to_type_models(types)
    model_names = [model.__name__ for model in type_models]
    type_union_queries = []

    def _get_tasks_in_cycle(model):
        """Filter tasks with particular statuses and cycle.

    Filtering tasks with statuses "Assigned", "In Progress" and "Finished".
    Where the task is in current users cycle.
    """
        task_query = db.session.query(
            model.id.label('id'),
            literal(model.__name__).label('type'),
            literal(None).label('context_id'),
        ).join(Cycle, Cycle.id == model.cycle_id).join(
            all_models.AccessControlList,
            sa.and_(
                all_models.AccessControlList.object_type ==
                all_models.CycleTaskGroupObjectTask.__name__,
                all_models.AccessControlList.object_id ==
                all_models.CycleTaskGroupObjectTask.id,
                all_models.AccessControlList.person_id == contact_id,
            ),
        ).join(all_models.AccessControlRole,
               sa.and_(
                   all_models.AccessControlRole.id ==
                   all_models.AccessControlList.ac_role_id,
                   all_models.AccessControlRole.object_type ==
                   all_models.CycleTaskGroupObjectTask.__name__,
                   all_models.AccessControlRole.name.in_(
                       ("Task Assignees", "Task Secondary Assignees")),
               )).filter(Cycle.is_current == true(), )
        return task_query.filter(
            Cycle.is_verification_needed == true(),
            model.status.in_([
                all_models.CycleTaskGroupObjectTask.ASSIGNED,
                all_models.CycleTaskGroupObjectTask.IN_PROGRESS,
                all_models.CycleTaskGroupObjectTask.FINISHED,
                all_models.CycleTaskGroupObjectTask.DECLINED,
                all_models.CycleTaskGroupObjectTask.DEPRECATED,
            ])).union_all(
                task_query.filter(
                    Cycle.is_verification_needed == false(),
                    model.status.in_([
                        all_models.CycleTaskGroupObjectTask.ASSIGNED,
                        all_models.CycleTaskGroupObjectTask.IN_PROGRESS,
                        all_models.CycleTaskGroupObjectTask.DEPRECATED,
                    ])))

    def _get_model_specific_query(model):
        """Prepare query specific for a particular model."""
        model_type_query = None
        if model is all_models.CycleTaskGroupObjectTask:
            model_type_query = _get_tasks_in_cycle(model)
        return model_type_query

    type_union_queries.extend((
        _get_object_mapped_ca(contact_id, model_names),
        _get_custom_roles(contact_id, model_names),
    ))

    for model in type_models:
        query = _get_model_specific_query(model)
        if query:
            type_union_queries.append(query)

        if model is all_models.Workflow:
            type_union_queries.append(backlog_workflows())
        if model is all_models.Person:
            type_union_queries.append(_get_people())

    return alias(union(*type_union_queries))
