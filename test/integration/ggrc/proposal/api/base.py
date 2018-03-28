# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Base TestCase for proposal api."""

import contextlib

from ggrc.models import all_models

from integration.ggrc import TestCase
from integration.ggrc.api_helper import Api


class BaseTestProposalApi(TestCase):
    """Base TestCase class proposal apip tests."""

    def setUp(self):
        super(BaseTestProposalApi, self).setUp()
        self.api = Api()
        self.client.get("/login")

    def create_proposal(self, instance, **context):
        """Create proposal."""
        data = context.copy()
        data["instance"] = {"id": instance.id, "type": instance.type}
        resp = self.api.post(all_models.Proposal, {"proposal": data})
        self.assertEqual(201, resp.status_code)
        return resp

    def update_proposal_status(self, proposal, status, resp_status, **context):
        """Update proposal status via api."""
        data = {"status": status}
        data.update(context)
        resp = self.api.put(proposal, {"proposal": data})
        self.assertEqual(resp_status, resp.status_code)
        return resp

    def decline_proposal(self, proposal, resp_status=200, **context):
        return self.update_proposal_status(proposal, proposal.STATES.DECLINED,
                                           resp_status, **context)

    def apply_proposal(self, proposal, resp_status=200, **context):
        return self.update_proposal_status(proposal, proposal.STATES.APPLIED,
                                           resp_status, **context)

    @staticmethod
    def revision_query_for(obj):
        return all_models.Revision.query.filter(
            all_models.Revision.resource_type == obj.type,
            all_models.Revision.resource_id == obj.id)

    def latest_revision_for(self, obj):
        return self.revision_query_for(obj).order_by(
            all_models.Revision.id.desc()).first()

    @contextlib.contextmanager
    def number_obj_revisions_for(self, obj, increase_on=1):
        """Context manager,

    checks the number of logged revisions after nested operations."""
        revision_query = self.revision_query_for(obj)
        start_count = revision_query.count()
        yield
        expected = start_count + increase_on
        current = revision_query.count()
        msg = ("Object change isn't logged correctly: "
               "expected number {expected} is not equal to {current}.")
        self.assertEqual(expected, current,
                         msg.format(expected=expected, current=current))
