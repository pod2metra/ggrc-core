# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Defines a Revision model for storing snapshots."""

import sqlalchemy as sa

from ggrc import db
from ggrc.models import mixins
from ggrc.models import reflection
from ggrc.models import relationship
from ggrc.models import types
from ggrc.models import utils
from ggrc.fulltext import mixin as ft_mixin
from ggrc.utils import referenced_objects
from ggrc.access_control import list as ac_list
from ggrc.access_control import roleable
from ggrc.access_control import role as ac_role
from ggrc.utils.revisions_diff import builder
from ggrc import settings
from ggrc.models import comment

# pylint: disable=too-few-public-methods


class FullInstanceContentFased(utils.FasadeProperty):
  """Custom fasade property for full_instance_content property."""

  FIELD_NAME = "content"

  def prepare(self, data):
    data = super(FullInstanceContentFased, self).prepare(data)
    return builder.prepare(
        referenced_objects.get(data["instance"]["type"],
                               data["instance"]["id"]),
        data["full_instance_content"])


# pylint: enable=too-few-public-methods


class Proposalable(object):  # pylint: disable=too-few-public-methods
  """Mixin to setup instance as proposable."""

  @sa.ext.declarative.declared_attr
  def proposals(cls):  # pylint: disable=no-self-argument
    """declare proposals relationship for proposable instance."""
    def join_function():
      return sa.and_(
          sa.orm.foreign(Proposal.instance_type) == cls.__name__,
          sa.orm.foreign(Proposal.instance_id) == cls.id,
      )

    return sa.orm.relationship(
        Proposal,
        primaryjoin=join_function,
        backref=Proposal.INSTANCE_TMPL.format(cls.__name__),
    )


class Proposal(mixins.person_relation_factory("applied_by"),
               mixins.person_relation_factory("declined_by"),
               mixins.person_relation_factory("proposed_by"),
               comment.CommentInitiator,
               mixins.Stateful,
               roleable.Roleable,
               relationship.Relatable,
               mixins.Base,
               ft_mixin.Indexed,
               db.Model):
  """Proposal model.

  Collect all information about propose change to Proposable instances."""

  __tablename__ = 'proposals'

  # pylint: disable=too-few-public-methods
  class NotificationContext(object):
    DIGEST_TITLE = "Proposal Digest"
    DIGEST_TMPL = settings.JINJA2.get_template(
        "notifications/proposal_digest.html")

  class ACRoles(object):
    READER = "ProposalReader"
    EDITOR = "ProposalEditor"

  class STATES(object):
    """All states for proposals."""
    PROPOSED = "proposed"
    APPLIED = "applied"
    DECLINED = "declined"

  class CommentTemplatesTextBuilder(object):
    """Temapltes for comments for proposals."""
    PROPOSED_WITH_AGENDA = ("<p>Proposal has been created with comment: "
                            "{text}</p>")
    APPLIED_WITH_COMMENT = ("<p>Proposal created by {user} has been applied "
                            "with a comment: {text}</p>")
    DECLINED_WITH_COMMENT = ("<p>Proposal created by {user} has been declined "
                             "with a comment: {text}</p>")

    PROPOSED_WITHOUT_AGENDA = "<p>Proposal has been created.</p>"
    APPLIED_WITHOUT_COMMENT = ("<p>Proposal created by {user} "
                               "has been applied.</p>")
    DECLINED_WITHOUT_COMMENT = ("<p>Proposal created by {user} "
                                "has been declined.</p>")
  # pylint: enable=too-few-public-methods

  def build_comment_text(self, reason, text, proposed_by):
    """Build proposal comment dependable from proposal state."""
    if reason == self.STATES.PROPOSED:
      with_tmpl = self.CommentTemplatesTextBuilder.PROPOSED_WITH_AGENDA
      without_tmpl = self.CommentTemplatesTextBuilder.PROPOSED_WITHOUT_AGENDA
    elif reason == self.STATES.APPLIED:
      with_tmpl = self.CommentTemplatesTextBuilder.APPLIED_WITH_COMMENT
      without_tmpl = self.CommentTemplatesTextBuilder.APPLIED_WITHOUT_COMMENT
    elif reason == self.STATES.DECLINED:
      with_tmpl = self.CommentTemplatesTextBuilder.DECLINED_WITH_COMMENT
      without_tmpl = self.CommentTemplatesTextBuilder.DECLINED_WITHOUT_COMMENT
    tmpl = with_tmpl if text else without_tmpl
    return tmpl.format(user=proposed_by.email, text=text)

  VALID_STATES = [STATES.PROPOSED, STATES.APPLIED, STATES.DECLINED]

  instance_id = db.Column(db.Integer, nullable=False)
  instance_type = db.Column(db.String, nullable=False)
  content = db.Column('content', types.LongJsonType, nullable=False)
  agenda = db.Column(db.Text, nullable=False, default=u"")
  decline_reason = db.Column(db.Text, nullable=False, default=u"")
  decline_datetime = db.Column(db.DateTime, nullable=True)
  apply_reason = db.Column(db.Text, nullable=False, default=u"")
  apply_datetime = db.Column(db.DateTime, nullable=True)
  proposed_notified_datetime = db.Column(db.DateTime, nullable=True)

  INSTANCE_TMPL = "{}_proposalable"

  instance = utils.json_polimorphic_relationship_factory(
      Proposalable
  )(
      "instance_id", "instance_type", INSTANCE_TMPL
  )

  _fulltext_attrs = [
      "instance_id",
      "instance_type",
      "agenda",
      "decline_reason",
      "decline_datetime",
      "apply_reason",
      "apply_datetime",
  ]

  _api_attrs = reflection.ApiAttributes(
      reflection.Attribute("instance", update=False),
      reflection.Attribute("content", create=False, update=False),
      reflection.Attribute("agenda", update=False),
      # ignore create proposal in specific state to be shure
      # new proposal will be only in proposed state
      reflection.Attribute('status', create=False),
      reflection.Attribute('decline_reason', create=False),
      reflection.Attribute('decline_datetime', create=False, update=False),
      reflection.Attribute('declined_by', create=False, update=False),
      reflection.Attribute('apply_reason', create=False),
      reflection.Attribute('apply_datetime', create=False, update=False),
      reflection.Attribute('applied_by', create=False, update=False),
      reflection.Attribute('full_instance_content',
                           create=True,
                           update=False,
                           read=False),
      reflection.Attribute('proposed_by', create=False, update=False),
  )

  full_instance_content = FullInstanceContentFased()

  @staticmethod
  def _extra_table_args(_):
    return (db.Index("fk_instance", "instance_id", "instance_type"),
            db.Index("ix_decline_datetime", "decline_datetime"),
            db.Index("ix_apply_datetime", "apply_datetime"),
            db.Index("ix_proposed_notified_datetime",
                     "proposed_notified_datetime"))


def get_propsal_acr_dict():
  return {
      r.name: r for r in
      ac_role.AccessControlRole.query.filter(
          ac_role.AccessControlRole.object_type == Proposal.__name__,
          ac_role.AccessControlRole.name.in_([Proposal.ACRoles.EDITOR,
                                              Proposal.ACRoles.READER]))
  }


def permissions_for_proposal_setter(proposal, proposal_roles):
  """Append required proposal roles ACL to proposal."""
  parents = {a.parent for a in proposal.full_access_control_list}
  for acl in proposal.instance.full_access_control_list:
    if acl in parents:
      continue
    if acl.ac_role.update:
      role = proposal_roles[Proposal.ACRoles.EDITOR]
    elif acl.ac_role.read:
      role = proposal_roles[Proposal.ACRoles.READER]
    else:
      continue
    ac_list.AccessControlList(ac_role=role,
                              object=proposal,
                              person=acl.person,
                              parent=acl)


def set_acl_to_all_proposals_for(instance):
  if isinstance(instance, Proposalable):
    if isinstance(instance, roleable.Roleable):
      proposal_roles = get_propsal_acr_dict()
      for proposal in instance.proposals:
        permissions_for_proposal_setter(proposal, proposal_roles)


def set_acl_to(proposal):
  if isinstance(proposal, Proposal):
    if isinstance(proposal.instance, roleable.Roleable):
      permissions_for_proposal_setter(proposal, get_propsal_acr_dict())
