# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Evidence RBAC Factory."""

from ggrc.models import all_models
from integration.ggrc import Api, generator
from integration.ggrc.access_control.rbac_factories import base
from integration.ggrc.models import factories


class EvidenceRBACFactory(base.BaseRBACFactory):
  """Evidence RBAC factory class."""

  def __init__(self, user_id, acr, parent=None):
    """Set up objects for Evidence permission tests.

    Args:
        user_id: Id of user under which all operations will be run.
        acr: Instance of ACR that should be assigned for tested user.
        parent: Model name in scope of which objects should be set up.
    """
    self.setup_program_scope(user_id, acr)

    with factories.single_commit():
      evidence = factories.EvidenceUrlFactory()
      if parent == "Audit":
        self.mapping_id = factories.RelationshipFactory(
            source=self.audit, destination=evidence
        ).id
      elif parent == "Assessment":
        self.mapping_id = factories.RelationshipFactory(
            source=self.assessment, destination=evidence
        ).id
    self.evidence_id = evidence.id
    self.parent = parent
    self.admin_acr_id = all_models.AccessControlRole.query.filter_by(
        name="Admin",
        object_type="Evidence",
    ).one().id
    self.user_id = user_id
    self.api = Api()
    self.objgen = generator.ObjectGenerator()
    self.objgen.api = self.api
    if user_id:
      user = all_models.Person.query.get(user_id)
      self.api.set_user(user)

  def create(self):
    """Create new Evidence object."""
    result = self.api.post(all_models.Evidence, {
        "evidence": {
            "access_control_list": [{
                "ac_role_id": self.admin_acr_id,
                "person": {
                    "id": self.user_id,
                    "type": "Person",
                }
            }],
            "link": factories.random_str(),
            "title": factories.random_str(),
            "context": None,
        }
    })
    return result

  def read(self):
    """Read existing Evidence object."""
    res = self.api.get(all_models.Evidence, self.evidence_id)
    return res

  def update(self):
    """Update title of existing Evidence object."""
    evidence = all_models.Evidence.query.get(self.evidence_id)
    return self.api.put(evidence, {"title": factories.random_str()})

  def delete(self):
    """Delete Evidence object."""
    evidence = all_models.Evidence.query.get(self.evidence_id)
    return self.api.delete(evidence)

  def map(self, evidence=None):
    """Map Evidence to parent object."""
    if self.parent == "Audit":
      parent = all_models.Audit.query.get(self.audit_id)
    else:
      parent = all_models.Assessment.query.get(self.assessment_id)
    map_evidence = evidence if evidence else factories.EvidenceUrlFactory()

    return self.objgen.generate_relationship(
        source=parent,
        destination=map_evidence
    )[0]

  def create_and_map(self):
    """Create new Evidence and map it to parent."""
    response = self.create()
    evidence_id = None
    if response.json and response.json.get("evidence"):
      evidence_id = response.json.get("evidence", {}).get("id")
    if not evidence_id:
      return response

    evidence = all_models.Evidence.query.get(evidence_id)
    return self.map(evidence)

  def add_comment(self):
    """Map new comment to evidence."""
    evidence = all_models.Evidence.query.get(self.evidence_id)
    return self.objgen.generate_object(all_models.Comment, {
        "description": factories.random_str(),
        "context": None,
        "related_to": evidence,
    })[0]

  def read_comments(self):
    """Read comments mapped to evidence"""
    evidence = all_models.Evidence.query.get(self.evidence_id)
    with factories.single_commit():
      comment = factories.CommentFactory(description=factories.random_str())
      factories.RelationshipFactory(source=evidence, destination=comment)

    query_request_data = [{
        "fields": [],
        "filters": {
            "expression": {
                "object_name": "Evidence",
                "op": {
                    "name": "relevant"
                },
                "ids": [evidence.id]
            }
        },
        "object_name": "Comment",
    }]

    response = self.api.send_request(
        self.api.client.post,
        data=query_request_data,
        api_link="/query"
    )
    return response
