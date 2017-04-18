# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Module contains a workflow Cycle model
"""

from sqlalchemy import orm

from ggrc import db
from ggrc.models.mixins import Described
from ggrc.models.mixins import Notifiable
from ggrc.models.mixins import Slugged
from ggrc.models.mixins import Stateful
from ggrc.models.mixins import Timeboxed
from ggrc.models.mixins import Titled
from ggrc.models.mixins import WithContact
from ggrc.fulltext.attributes import (
    MultipleSubpropertyFullTextAttr,
    DateMultipleSubpropertyFullTextAttr,
    DateFullTextAttr,
)
from ggrc.fulltext.mixin import Indexed, ReindexRule


class Cycle(WithContact, Stateful, Timeboxed, Described, Titled, Slugged,
            Notifiable, Indexed, db.Model):
  """Workflow Cycle model
  """
  __tablename__ = 'cycles'
  _title_uniqueness = False

  VALID_STATES = (u'Assigned', u'InProgress', u'Finished', u'Verified')

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

  _publish_attrs = [
      'workflow',
      'cycle_task_groups',
      'is_current',
      'next_due_date',
  ]

  _aliases = {
      "cycle_workflow": {
          "display_name": "Workflow",
          "filter_by": "_filter_by_cycle_workflow",
      },
      "status": {
          "display_name": "State",
          "mandatory": False,
          "description": "Options are: \n{} ".format('\n'.join(VALID_STATES))
      }
  }

  PROPERTY_TEMPLATE = u"cycle {}"

  _fulltext_attrs = [
      MultipleSubpropertyFullTextAttr(
          "group title", "cycle_task_groups", ["title"], False,
      ),
      MultipleSubpropertyFullTextAttr(
          "group assignee",
          lambda instance: [g.contact for g in instance.cycle_task_groups],
          ["name", "email"],
          False,
      ),
      DateMultipleSubpropertyFullTextAttr(
          "group due date",
          'cycle_task_groups',
          ["next_due_date"],
          False,
      ),
      MultipleSubpropertyFullTextAttr(
          "task title",
          'cycle_task_group_object_tasks',
          ["title"],
          False,
      ),
      MultipleSubpropertyFullTextAttr(
          "task assignee",
          lambda instance: [t.contact for t in
                            instance.cycle_task_group_object_tasks],
          ["name", "email"],
          False
      ),
      DateMultipleSubpropertyFullTextAttr(
          "task due date",
          "cycle_task_group_object_tasks",
          ["end_date"],
          False
      ),
      DateFullTextAttr("due date", "next_due_date"),
  ]

  AUTO_REINDEX_RULES = [
      ReindexRule("CycleTaskGroup", lambda x: x.cycle),
      ReindexRule("CycleTaskGroupObjectTask",
                  lambda x: x.cycle_task_group.cycle),
      ReindexRule("Person",
                  lambda x: Cycle.query.filter(Cycle.contact_id == x.id))
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
