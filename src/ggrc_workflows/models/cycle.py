# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Module contains a workflow Cycle model
"""

import itertools
from sqlalchemy import orm, inspect

from ggrc import db
from ggrc.models import mixins
from ggrc.models import reflection
from ggrc.fulltext import attributes as ft_attributes
from ggrc.fulltext import mixin as ft_mixin

from ggrc_workflows.models import mixins as wf_mixins


def _query_filtered_by_contact(person):
  """Returns cycle required to reindex for sent persons."""
  attrs = inspect(person).attrs
  if any([attrs["email"].history.has_changes(),
          attrs["name"].history.has_changes()]):
    return Cycle.query.filter(Cycle.contact_id == person.id)
  else:
    return []


class Cycle(mixins.WithContact,
            wf_mixins.CycleStatusValidatedMixin,
            mixins.Timeboxed,
            mixins.Described,
            mixins.Titled,
            mixins.Slugged,
            mixins.Notifiable,
            ft_mixin.Indexed,
            db.Model):
  """Workflow Cycle model
  """
  __tablename__ = 'cycles'
  _title_uniqueness = False

  workflow_id = db.Column(
      db.Integer,
      db.ForeignKey('workflows.id', ondelete="CASCADE"),
      nullable=False,
  )
  cycle_task_groups = db.relationship(
      'CycleTaskGroup', backref='cycle', cascade='all, delete-orphan')
  cycle_task_group_object_tasks = db.relationship(
      'CycleTaskGroupObjectTask', backref='cycle',
      cascade='all, delete-orphan')
  cycle_task_entries = db.relationship(
      'CycleTaskEntry', backref='cycle', cascade='all, delete-orphan')
  is_current = db.Column(db.Boolean, default=True, nullable=False)
  next_due_date = db.Column(db.Date)

  _api_attrs = reflection.ApiAttributes(
      'workflow',
      'cycle_task_groups',
      'is_current',
      'next_due_date',
  )

  _aliases = {
      "cycle_workflow": {
          "display_name": "Workflow",
          "filter_by": "_filter_by_cycle_workflow",
      },
      "contact": "Assignee",
      "secondary_contact": None,
  }

  PROPERTY_TEMPLATE = u"cycle {}"

  _fulltext_attrs = [
      ft_attributes.MultipleSubpropertyFullTextAttr(
          "group title", "cycle_task_groups", ["title"], False,
      ),
      ft_attributes.MultipleSubpropertyFullTextAttr(
          "group assignee",
          lambda instance: [g.contact for g in instance.cycle_task_groups],
          ["name", "email"],
          False,
      ),
      ft_attributes.DateMultipleSubpropertyFullTextAttr(
          "group due date",
          'cycle_task_groups',
          ["next_due_date"],
          False,
      ),
      ft_attributes.MultipleSubpropertyFullTextAttr(
          "task title",
          'cycle_task_group_object_tasks',
          ["title"],
          False,
      ),
      ft_attributes.MultipleSubpropertyFullTextAttr(
          "task assignee",
          lambda instance: [t.contact for t in
                            instance.cycle_task_group_object_tasks],
          ["name", "email"],
          False
      ),
      ft_attributes.DateMultipleSubpropertyFullTextAttr(
          "task due date",
          "cycle_task_group_object_tasks",
          ["end_date"],
          False
      ),
      ft_attributes.DateFullTextAttr("due date", "next_due_date"),
      ft_attributes.MultipleSubpropertyFullTextAttr(
          "task comments",
          lambda instance: list(itertools.chain(*[
              t.cycle_task_entries
              for t in instance.cycle_task_group_object_tasks
          ])),
          ["description"],
          False
      ),
  ]

  AUTO_REINDEX_RULES = [
      ft_mixin.ReindexRule("CycleTaskGroup", lambda x: x.cycle),
      ft_mixin.ReindexRule("CycleTaskGroupObjectTask",
                           lambda x: x.cycle_task_group.cycle),
      ft_mixin.ReindexRule("Person", _query_filtered_by_contact)
  ]

  @classmethod
  def _filter_by_cycle_workflow(cls, predicate):
    from ggrc_workflows.models.workflow import Workflow
    return Workflow.query.filter(
        (Workflow.id == cls.workflow_id) &
        (predicate(Workflow.slug) | predicate(Workflow.title))
    ).exists()

  @classmethod
  def eager_query(cls):
    """Add cycle task groups to cycle eager query

    This function adds cycle_task_groups as a join option when fetching cycles,
    and makes sure we fetch all cycle related data needed for generating cycle
    json, in one query.

    Returns:
      a query object with cycle_task_groups added to joined load options.
    """
    query = super(Cycle, cls).eager_query()
    return query.options(
        orm.joinedload('cycle_task_groups'),
    )

  @classmethod
  def indexed_query(cls):
    return super(Cycle, cls).indexed_query().options(
        orm.Load(cls).load_only("next_due_date"),
        orm.Load(cls).subqueryload("cycle_task_group_object_tasks").load_only(
            "id",
            "title",
            "end_date"
        ),
        orm.Load(cls).subqueryload("cycle_task_groups").load_only(
            "id",
            "title",
            "end_date",
            "next_due_date",
        ),
        orm.Load(cls).subqueryload("cycle_task_group_object_tasks").joinedload(
            "contact"
        ).load_only(
            "email",
            "name",
            "id"
        ),
        orm.Load(cls).subqueryload("cycle_task_group_object_tasks").joinedload(
            "cycle_task_entries"
        ).load_only(
            "description",
            "id"
        ),
        orm.Load(cls).subqueryload("cycle_task_groups").joinedload(
            "contact"
        ).load_only(
            "email",
            "name",
            "id"
        ),
        orm.Load(cls).joinedload("contact").load_only(
            "email",
            "name",
            "id"
        ),
    )
