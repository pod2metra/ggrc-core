# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Module for cycle task group model.
"""

from sqlalchemy import orm

from ggrc import db
from ggrc.models.mixins import Base
from ggrc.models.mixins import Described
from ggrc.models.mixins import Slugged
from ggrc.models.mixins import Stateful
from ggrc.models.mixins import Timeboxed
from ggrc.models.mixins import Titled
from ggrc.models.mixins import WithContact
from ggrc_workflows.models.cycle import Cycle
from ggrc.fulltext.mixin import Indexed, ReindexRule
from ggrc.fulltext.attributes import (
    MultipleSubpropertyFullTextAttr,
    DateMultipleSubpropertyFullTextAttr,
    FullTextAttr,
    DateFullTextAttr,
)


class CycleTaskGroup(WithContact, Stateful, Slugged, Timeboxed, Described,
                     Titled, Base, Indexed, db.Model):
  """Cycle Task Group model.
  """
  __tablename__ = 'cycle_task_groups'
  _title_uniqueness = False

  @classmethod
  def generate_slug_prefix_for(cls, obj):
    return "CYCLEGROUP"

  VALID_STATES = (
      u'Assigned', u'InProgress', u'Finished', u'Verified', u'Declined')

  cycle_id = db.Column(
      db.Integer,
      db.ForeignKey('cycles.id', ondelete="CASCADE"),
      nullable=False,
  )
  task_group_id = db.Column(
      db.Integer, db.ForeignKey('task_groups.id'), nullable=True)
  cycle_task_group_tasks = db.relationship(
      'CycleTaskGroupObjectTask',
      backref='cycle_task_group',
      cascade='all, delete-orphan'
  )
  sort_index = db.Column(
      db.String(length=250), default="", nullable=False)
  next_due_date = db.Column(db.Date)

  _publish_attrs = [
      'cycle',
      'task_group',
      'cycle_task_group_tasks',
      'sort_index',
      'next_due_date'
  ]

  _aliases = {
      "cycle": {
          "display_name": "Cycle",
          "filter_by": "_filter_by_cycle",
      },
  }

  PROPERTY_TEMPLATE = u"group {}"

  _fulltext_attrs = [
      MultipleSubpropertyFullTextAttr(
          "task title", 'cycle_task_group_tasks', ["title"], False
      ),
      MultipleSubpropertyFullTextAttr(
          "task assignee",
          lambda instance: [t.contact for t in
                            instance.cycle_task_group_tasks],
          ["name", "email"],
          False
      ),
      DateMultipleSubpropertyFullTextAttr(
          "task due date", "cycle_task_group_tasks", ["end_date"], False
      ),
      DateFullTextAttr("due date", 'next_due_date',),
      FullTextAttr("assignee", "contact", ['name', 'email']),
      FullTextAttr("cycle title", 'cycle', ['title'], False),
      FullTextAttr("cycle assignee",
                   lambda x: x.cycle.contact,
                   ['email', 'name'], False),
      DateFullTextAttr("cycle due date",
                       lambda x: x.cycle.next_due_date,
                       with_template=False),
  ]

  AUTO_REINDEX_RULES = [
      ReindexRule("CycleTaskGroupObjectTask", lambda x: x.cycle_task_group),
      ReindexRule(
          "Person",
          lambda x: CycleTaskGroup.query.filter(
              CycleTaskGroup.contact_id == x.id)
      ),
      ReindexRule(
          "Person",
          lambda x: [i.cycle for i in CycleTaskGroup.query.filter(
              CycleTaskGroup.contact_id == x.id)]
      ),
  ]

  @classmethod
  def _filter_by_cycle(cls, predicate):
    """Get query that filters cycle task groups.

    Args:
      predicate: lambda function that excepts a single parameter and returns
      true of false.

    Returns:
      An sqlalchemy query that evaluates to true or false and can be used in
      filtering cycle task groups by related cycle.
    """
    return Cycle.query.filter(
        (Cycle.id == cls.cycle_id) &
        (predicate(Cycle.slug) | predicate(Cycle.title))
    ).exists()

  @classmethod
  def indexed_query(cls):
    return super(CycleTaskGroup, cls).indexed_query().options(
        orm.Load(cls).load_only(
            "next_due_date",
        ),
        orm.Load(cls).subqueryload("cycle_task_group_tasks").load_only(
            "id",
            "title",
            "end_date"
        ),
        orm.Load(cls).joinedload("cycle").load_only(
            "id",
            "title",
            "next_due_date"
        ),
        orm.Load(cls).subqueryload("cycle_task_group_tasks").joinedload(
            "contact"
        ).load_only(
            "email",
            "name",
            "id"
        ),
        orm.Load(cls).joinedload("cycle").joinedload(
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

  @classmethod
  def eager_query(cls):
    """Add cycle tasks and objects to cycle task group eager query.

    Make sure we load all cycle task group relevant data in a single query.

    Returns:
      a query object with cycle_task_group_tasks added to joined load options.
    """
    query = super(CycleTaskGroup, cls).eager_query()
    return query.options(
        orm.joinedload('cycle_task_group_tasks')
    )
