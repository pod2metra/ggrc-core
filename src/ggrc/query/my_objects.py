# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""This module helper query builder for my dashboard page."""
from sqlalchemy import and_
from sqlalchemy import literal
from sqlalchemy import or_
from sqlalchemy import true, false
from sqlalchemy import union
from sqlalchemy import alias
from sqlalchemy.orm import aliased
from ggrc import db
from ggrc.models import all_models
from ggrc.models.object_person import ObjectPerson
from ggrc.models.relationship import Relationship
from ggrc.models.custom_attribute_value import CustomAttributeValue
from ggrc.query import utils as query_utils
from ggrc_basic_permissions import backlog_workflows
from ggrc_basic_permissions.models import UserRole, Role
from ggrc_workflows.models import Cycle


def _types_to_type_models(types):
  """Convert string types to real objects."""
  if types is None:
    return all_models.all_models
  return [m for m in all_models.all_models if m.__name__ in types]


def get_myobjects_query(types=None, contact_id=None, is_creator=False):  # noqa
  """Filters by "myview" for a given person.

  Finds all objects which might appear on a user's Profile or Dashboard
  pages.

  This method only *limits* the result set -- Contexts and Roles will still
  filter out forbidden objects.
  """
  type_models = _types_to_type_models(types)
  model_names = [model.__name__ for model in type_models]
  type_union_queries = []

  def _get_people():
    """Get all the people w/o any restrictions."""
    all_people = db.session.query(
        all_models.Person.id.label('id'),
        literal(all_models.Person.__name__).label('type'),
        literal(None).label('context_id')
    )
    return all_people

  def _get_object_people():
    """Objects to which the user is 'mapped'."""
    object_people_query = db.session.query(
        ObjectPerson.personable_id.label('id'),
        ObjectPerson.personable_type.label('type'),
        literal(None).label('context_id')
    ).filter(
        and_(
            ObjectPerson.person_id == contact_id,
            ObjectPerson.personable_type.in_(model_names)
        )
    )
    return object_people_query

  def _get_object_owners():
    """Objects for which the user is an 'owner'."""
    object_owners_query = db.session.query(
        all_models.AccessControlList.object_id.label('id'),
        all_models.AccessControlList.object_type.label('type'),
        literal(None).label('context_id')
    ).filter(
        and_(
            all_models.AccessControlList.person_id == contact_id,
            all_models.AccessControlList.object_type.in_(model_names),
            all_models.AccessControlRole.name == "Admin"
        )
    )
    return object_owners_query

  def _get_object_mapped_ca():
    """Objects to which the user is mapped via a custom attribute."""
    ca_mapped_objects_query = db.session.query(
        CustomAttributeValue.attributable_id.label('id'),
        CustomAttributeValue.attributable_type.label('type'),
        literal(None).label('context_id')
    ).filter(
        and_(
            CustomAttributeValue.attribute_value == "Person",
            CustomAttributeValue.attribute_object_id == contact_id,
            CustomAttributeValue.attributable_type.in_(model_names)
        )
    )
    return ca_mapped_objects_query

  def _get_objects_user_assigned():
    """Objects for which the user is assigned."""
    dst_assignee_query = db.session.query(
        Relationship.destination_id.label('id'),
        Relationship.destination_type.label('type'),
        literal(None).label('context_id'),
    ).filter(
        and_(
            Relationship.source_type == "Person",
            Relationship.source_id == contact_id,
            Relationship.destination_type.in_(model_names)
        ),
    )
    src_assignee_query = db.session.query(
        Relationship.source_id.label('id'),
        Relationship.source_type.label('type'),
        literal(None).label('context_id'),
    ).filter(
        and_(
            Relationship.destination_type == "Person",
            Relationship.destination_id == contact_id,
            Relationship.source_type.in_(model_names)
        ),
    )
    return dst_assignee_query.union(src_assignee_query)

  def _get_results_by_context(model):
    """Objects based on the context of the current model.

    Return the objects that are in private contexts via UserRole.
    """
    context_query = db.session.query(
        model.id.label('id'),
        literal(model.__name__).label('type'),
        literal(None).label('context_id'),
    ).join(
        UserRole,
        and_(
            UserRole.context_id == model.context_id,
            UserRole.person_id == contact_id,
        )
    )
    return context_query

  def _get_assigned_to_records(model):
    """Get query by models contacts fields.

    Objects for which the user is the 'contact' or 'secondary contact'.
    Control also has 'principal_assessor' and 'secondary_assessor'.
    """
    model_type_queries = []
    for attr in ('contact_id', 'secondary_contact_id',
                 'principal_assessor_id', 'secondary_assessor_id'):
      if hasattr(model, attr):
        model_type_queries.append(getattr(model, attr) == contact_id)
    return model_type_queries

  def _get_tasks_in_cycle(model):
    """Filter tasks with particular statuses and cycle.

    Filtering tasks with statuses "Assigned", "InProgress" and "Finished".
    Where the task is in current users cycle.
    """
    task_query = db.session.query(
        model.id.label('id'),
        literal(model.__name__).label('type'),
        literal(None).label('context_id'),
    ).join(
        Cycle,
        Cycle.id == model.cycle_id
    ).filter(
        Cycle.is_current == true(),
        model.contact_id == contact_id
    )
    return task_query.filter(
        Cycle.is_verification_needed == true(),
        model.status.in_([
            all_models.CycleTaskGroupObjectTask.ASSIGNED,
            all_models.CycleTaskGroupObjectTask.IN_PROGRESS,
            all_models.CycleTaskGroupObjectTask.FINISHED,
            all_models.CycleTaskGroupObjectTask.DECLINED,
        ])
    ).union_all(
        task_query.filter(
            Cycle.is_verification_needed == false(),
            model.status.in_([
                all_models.CycleTaskGroupObjectTask.ASSIGNED,
                all_models.CycleTaskGroupObjectTask.IN_PROGRESS,
            ])
        )
    )

  def _get_model_specific_query(model):
    """Prepare query specific for a particular model."""
    model_type_query = None
    if model is all_models.CycleTaskGroupObjectTask:
      model_type_query = _get_tasks_in_cycle(model)
    else:
      model_type_queries = _get_assigned_to_records(model)
      if model_type_queries:
        type_column = query_utils.get_type_select_column(model)
        model_type_query = db.session.query(
            model.id.label('id'),
            type_column.label('type'),
            literal(None).label('context_id')
        ).filter(or_(*model_type_queries)).distinct()
    return model_type_query

  def _get_context_relationships():
    """Load list of objects related on contexts and objects types.

    This code handles the case when user is added as `Auditor` and should be
    able to see objects mapped to the `Program` on `My Work` page.

    Returns:
      objects (list((id, type, None))): Related objects
    """
    user_role_query = db.session.query(UserRole.context_id).join(
        Role, UserRole.role_id == Role.id).filter(and_(
            UserRole.person_id == contact_id, Role.name == 'Auditor')
    )

    _ct = aliased(all_models.Context, name="c")
    _rl = aliased(all_models.Relationship, name="rl")
    context_query = db.session.query(
        _rl.source_id.label('id'),
        _rl.source_type.label('type'),
        literal(None)).join(_ct, and_(
            _ct.id.in_(user_role_query),
            _rl.destination_id == _ct.related_object_id,
            _rl.destination_type == _ct.related_object_type,
            _rl.source_type.in_(model_names),
        )).union(db.session.query(
            _rl.destination_id.label('id'),
            _rl.destination_type.label('type'),
            literal(None)).join(_ct, and_(
                _ct.id.in_(user_role_query),
                _rl.source_id == _ct.related_object_id,
                _rl.source_type == _ct.related_object_type,
                _rl.destination_type.in_(model_names),)))

    return context_query

  def _get_custom_roles():
    """Objects for which the user is an 'owner'."""
    custom_roles_query = db.session.query(
        all_models.AccessControlList.object_id.label('id'),
        all_models.AccessControlList.object_type.label('type'),
        literal(None).label('context_id')
    ).join(
        all_models.AccessControlRole,
        all_models.AccessControlList.ac_role_id ==
        all_models.AccessControlRole.id
    ).filter(
        and_(
            all_models.AccessControlList.person_id == contact_id,
            all_models.AccessControlList.object_type.in_(model_names),
            all_models.AccessControlRole.my_work == true(),
            all_models.AccessControlRole.read == true()
        )
    )
    return custom_roles_query

  # Note: We don't return mapped objects for the Creator because being mapped
  # does not give the Creator necessary permissions to view the object.
  if not is_creator:
    type_union_queries.append(_get_object_people())

  type_union_queries.extend((_get_object_owners(),
                            _get_object_mapped_ca(),
                            _get_objects_user_assigned(),
                            _get_context_relationships(),
                            _get_custom_roles(),))

  for model in type_models:
    query = _get_model_specific_query(model)
    if query:
      type_union_queries.append(query)

    if model is all_models.Workflow:
      type_union_queries.append(backlog_workflows())
    if model is all_models.Person:
      type_union_queries.append(_get_people())
    if model in (all_models.Program, all_models.Audit, all_models.Workflow):
      type_union_queries.append(_get_results_by_context(model))

  return alias(union(*type_union_queries))
