# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""TestCase for proposal property api."""

from ggrc.models import all_models

from integration.ggrc.models import factories
from integration.ggrc.proposal.api import base


class TestPropoertyProposals(base.BaseTestProposalApi):
    """Test case for proposal property api."""

    def test_simple_get_proposal(self):
        """Test simple get proposal."""
        with factories.single_commit():
            control = factories.ControlFactory()
            proposal = factories.ProposalFactory(
                instance=control,
                content={"field": "a"},
                agenda="agenda content")
        instance_dict = {"id": control.id, "type": control.type}
        resp = self.api.get(all_models.Proposal, proposal.id)
        self.assert200(resp)
        self.assertIn("proposal", resp.json)
        data = resp.json["proposal"]
        self.assertIn("content", data)
        self.assertIn("instance", data)
        self.assertIn("agenda", data)
        self.assertDictEqual(instance_dict, data["instance"])
        self.assertDictEqual({"field": "a"}, data["content"])
        self.assertEqual("agenda content", data["agenda"])

    def test_simple_create_proposal(self):
        """Test simple create proposal."""
        new_title = "2"
        control = factories.ControlFactory(title="1")
        control_id = control.id
        control.title = new_title
        self.assertEqual(0, len(control.comments))
        self.create_proposal(
            control,
            full_instance_content=control.log_json(),
            agenda="update title from 1 to 2",
            context=None)
        control = all_models.Control.query.get(control_id)
        self.assertEqual(1, len(control.proposals))
        self.assertIn("fields", control.proposals[0].content)
        self.assertEqual({
            "title": "2"
        }, control.proposals[0].content["fields"])
        self.assertEqual(1, len(control.comments))

    def test_simple_apply_status(self):
        """Test simple apply status."""
        with factories.single_commit():
            control = factories.ControlFactory(title="1")
            proposal = factories.ProposalFactory(
                instance=control,
                content={"fields": {
                    "title": "2"
                }},
                agenda="agenda content")
        control_id = control.id
        proposal_id = proposal.id
        self.assertEqual(proposal.STATES.PROPOSED, proposal.status)
        self.assertEqual(0, len(control.comments))
        with self.number_obj_revisions_for(control):
            self.apply_proposal(proposal, apply_reason="approved")
        control = all_models.Control.query.get(control_id)
        proposal = all_models.Proposal.query.get(proposal_id)

        self.assertEqual(proposal.STATES.APPLIED, proposal.status)
        self.assertEqual("2", control.title)
        self.assertEqual("2",
                         self.latest_revision_for(control).content['title'])
        self.assertEqual(1, len(control.comments))

    def test_simple_decline_status(self):
        """Test simple decline status."""
        with factories.single_commit():
            control = factories.ControlFactory(title="1")
            proposal = factories.ProposalFactory(
                instance=control,
                content={"fields": {
                    "title": "2"
                }},
                agenda="agenda content")
        control_id = control.id
        proposal_id = proposal.id
        self.assertEqual(proposal.STATES.PROPOSED, proposal.status)
        self.assertEqual(0, len(control.comments))
        with self.number_obj_revisions_for(control, increase_on=0):
            self.decline_proposal(proposal, decline_reason="declined bla")
        control = all_models.Control.query.get(control_id)
        proposal = all_models.Proposal.query.get(proposal_id)
        self.assertEqual(proposal.STATES.DECLINED, proposal.status)
        self.assertEqual("1", control.title)
        self.assertEqual(1, len(control.comments))
