# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

import collections
import datetime
import six

import sqlalchemy as sa

from ggrc import db
from ggrc import utils
from ggrc.models import mixins


@six.add_metaclass(utils.Singleton)
class ProtocolPool(set):

  def protocol_to_db(self):
    for instance, fact in self:
      instance.protocol_to_db(fact)
    self.clear()


class Protocol(mixins.Identifiable, db.Model):
  __tablename__ = 'protocol'

  resource_id = db.Column(db.Integer)
  resource_type = db.Column(db.String)
  fact = db.Column(db.String)
  created_at = db.Column(db.DateTime, default=db.text('current_timestamp'))

  @staticmethod
  def _extra_table_args(model):
    """Apply extra table args (like indexes) to model definition."""
    return (
        db.Index('ix_resource', 'resource_type', 'resource_id', 'fact'),
    )

  @property
  def resource_attr(self):
    return '{0}_resource'.format(self.resource_type)

  @property
  def resource(self):
    return getattr(self, self.resource_attr)

  @resource.setter
  def resource(self, value):
    if value:
      val_id, val_name = value.id, value.__class__.__name__
    else:
      val_id = val_name = None
    self.resource_id, self.resource_type = val_id, val_name
    return setattr(self, self.resource_attr, value)


class Protacolable(object):

  LAST_DATE_GETTER_FORMAT = "{fact}_date"
  FIRST_DATE_GETTER_FORMAT = "first_{fact}_date"
  DATES_GETTER_FORMAT = "{fact}_dates"

  @sa.ext.declarative.declared_attr
  def protocols(cls):  # pylint: disable=no-self-argument

    return sa.orm.relationship(
        "Protocol",
        primaryjoin=lambda: sa.and_(
            sa.orm.foreign(Protocol.resource_id) == cls.id,
            sa.orm.foreign(Protocol.resource_type) == cls.__name__,
        ),
        backref='{0}_datetime_log'.format(cls.__name__),
        order_by=Protocol.id,
        viewonly=True,
    )

  @property
  def _date_logs_map(self):
    data = collections.defaultdict(list)
    for log in self.protocols:
      data[log.fact.lower()].append(log.created_at or datetime.datetime.now())
    return data

  def _date_logs_for(self, fact):
    return self._date_logs_map[fact.lower()]

  def _last_date_log(self, fact):
    if self._date_logs_for(fact):
      return max(self._date_logs_for(fact))

  def _first_date_log(self, fact):
    if self._date_logs_for(fact):
      return min(self._date_logs_for(fact))

  _DATA_GETTER_MAPPER = {
      LAST_DATE_GETTER_FORMAT: _last_date_log.__name__,
      FIRST_DATE_GETTER_FORMAT: _first_date_log.__name__,
      DATES_GETTER_FORMAT: _date_logs_for.__name__,
  }

  def __getattr__(self, name):
    for format_str, function_name in self._DATA_GETTER_MAPPER.iteritems():
      starter, finisher = format_str.format(fact="|").split("|", 1)
      if name.startswith(starter) and name.endswith(finisher):
        fact = name[len(starter):-len(finisher)]
        return getattr(self, function_name)(fact.lower())
    superinstance = super(Protacolable, self)
    if hasattr(superinstance, "__getattr__"):
      return superinstance.__getattr__(name)
    raise AttributeError

  @classmethod
  def _populated_protocols(cls, query):
    return query.options(
        sa.orm.Load(cls).subqueryload(
            "protocols"
        ).undefer_group(
            "Protocol_complete"
        )
    )

  @classmethod
  def indexed_query(cls):
    return cls._populated_protocols(super(Protacolable, cls).indexed_query())

  @classmethod
  def eager_query(cls):
    return cls._populated_protocols(super(Protacolable, cls).eager_query())

  def protocol_to_pool(self):
    return

  def protocol_to_db(self, *facts):
    for fact in facts:
      self.protocols.append(Protocol(resource=self, fact=fact))


class StatusProtocolable(Protacolable, mixins.statusable.Statusable):

  def protocol_to_pool(self):
    if sa.inspect(self).attrs['status'].history.added:
      ProtocolPool().add((self, self.status))
    super(StatusProtocolable, self).protocol_to_pool()
