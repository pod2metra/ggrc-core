# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Test for proposal mapping api."""

import json

from ggrc import utils
from ggrc.models import all_models

from integration.ggrc.models import factories
from integration.ggrc.proposal.api import base


class TestMappingProposalsApi(base.BaseTestProposalApi):
    """Test for proposal mapping api."""

    def test_change_mapping(self):
        """Test create mapping proposal."""
        setuped_kind, update_kind = all_models.Option.query.filter(
            all_models.Option.role == "control_kind")[:2]
        control = factories.ControlFactory(title="1", kind=setuped_kind)
        control_id = control.id
        data = control.log_json()
        update_kind_json = update_kind.log_json()
        data["kind"] = update_kind_json
        self.create_proposal(
            control,
            full_instance_content=data,
            agenda="update kind",
            context=None)
        control = all_models.Control.query.get(control_id)
        self.assertEqual(1, len(control.proposals))
        self.assertIn("mapping_fields", control.proposals[0].content)
        self.assertIn("kind", control.proposals[0].content["mapping_fields"])
        self.assertEqual(
            json.loads(utils.as_json(update_kind_json)),
            control.proposals[0].content["mapping_fields"]["kind"])
        self.assertEqual(1, len(control.comments))

    def test_apply_mapping(self):
        """Test apply mapping proposal."""
        setuped_kind, update_kind = all_models.Option.query.filter(
            all_models.Option.role == "control_kind")[:2]
        with factories.single_commit():
            control = factories.ControlFactory(title="1", kind=setuped_kind)
            proposal = factories.ProposalFactory(
                instance=control,
                content={
                    "mapping_fields": {
                        "kind": {
                            "id": update_kind.id,
                            "type": update_kind.type,
                        },
                    },
                },
                agenda="agenda content")
        control_id = control.id
        proposal_id = proposal.id
        update_kind_id = update_kind.id
        self.assertEqual(0, len(control.comments))
        with self.number_obj_revisions_for(control):
            self.apply_proposal(proposal, apply_reason="approved")
        control = all_models.Control.query.get(control_id)
        self.assertEqual(
            all_models.Option.query.get(update_kind_id), control.kind)
        proposal = all_models.Proposal.query.get(proposal_id)
        self.assertEqual(proposal.STATES.APPLIED, proposal.status)
        latest_revision = self.latest_revision_for(control)
        self.assertIn("kind", latest_revision.content)
        self.assertIn("id", latest_revision.content["kind"])
        self.assertEqual(update_kind_id, latest_revision.content["kind"]["id"])
        self.assertEqual(1, len(control.comments))

    def test_change_mapping_to_empty(self):
        """Test create empty mapping proposal."""
        setuped_kind = all_models.Option.query.filter(
            all_models.Option.role == "control_kind").first()
        control = factories.ControlFactory(title="1", kind=setuped_kind)
        control.kind = None
        control_id = control.id
        self.create_proposal(
            control,
            full_instance_content=control.log_json(),
            agenda="update kind",
            context=None)
        control = all_models.Control.query.get(control_id)
        self.assertEqual(1, len(control.proposals))
        self.assertIn("mapping_fields", control.proposals[0].content)
        self.assertIn("kind", control.proposals[0].content["mapping_fields"])
        self.assertIsNone(
            control.proposals[0].content["mapping_fields"]["kind"])
        self.assertEqual(1, len(control.comments))

    def test_apply_empty_mapping(self):
        """Test apply empty mapping proposal."""
        setuped_kind = all_models.Option.query.filter(
            all_models.Option.role == "control_kind").first()
        with factories.single_commit():
            control = factories.ControlFactory(title="1", kind=setuped_kind)
            proposal = factories.ProposalFactory(
                instance=control,
                content={"mapping_fields": {
                    "kind": None
                }},
                agenda="agenda content")
        control_id = control.id
        proposal_id = proposal.id
        self.assertEqual(0, len(control.comments))
        with self.number_obj_revisions_for(control):
            self.apply_proposal(proposal, apply_reason="approved")
        control = all_models.Control.query.get(control_id)
        self.assertIsNone(control.kind)
        proposal = all_models.Proposal.query.get(proposal_id)
        self.assertEqual(proposal.STATES.APPLIED, proposal.status)
        latest_revision = self.latest_revision_for(control)
        self.assertIn("kind", latest_revision.content)
        self.assertIsNone(latest_revision.content["kind"])
        self.assertEqual(1, len(control.comments))
