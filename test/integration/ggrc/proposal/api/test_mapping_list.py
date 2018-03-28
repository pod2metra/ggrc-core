# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Test for proposal mapping list api."""

import json

from ggrc import utils
from ggrc.models import all_models

from integration.ggrc.models import factories
from integration.ggrc.proposal.api import base


class TestMappingListProposalsApi(base.BaseTestProposalApi):
    """Test for proposal mapping list api."""

    def test_change_mapping_list(self):
        """Test create mapping list proposal."""
        with factories.single_commit():
            cat = factories.ControlCategoryFactory()
            control = factories.ControlFactory(title="1")
        data = control.log_json()
        control_id = control.id
        data["categories"] = [{"id": cat.id, "type": cat.type}]
        cat_id = cat.id
        self.create_proposal(
            control,
            full_instance_content=data,
            agenda="update categories",
            context=None)
        control = all_models.Control.query.get(control_id)
        self.assertEqual(1, len(control.proposals))
        self.assertIn("mapping_list_fields", control.proposals[0].content)
        fields = control.proposals[0].content["mapping_list_fields"]
        self.assertIn("categories", fields)
        self.assertEqual({
            "added": [{
                "id": cat_id,
                "type": "ControlCategory"
            }],
            "deleted": []
        }, fields["categories"])
        self.assertEqual(1, len(control.comments))

    def test_change_empty_mapping_list(self):
        """Test create mapping list proposal to empty."""
        with factories.single_commit():
            category = factories.ControlCategoryFactory()
            control = factories.ControlFactory(categories=[category])
        data = control.log_json()
        category_id = category.id
        control_id = control.id
        data["categories"] = []
        self.create_proposal(
            control,
            full_instance_content=data,
            agenda="update categories",
            context=None)
        control = all_models.Control.query.get(control_id)
        category = all_models.ControlCategory.query.get(category_id)
        self.assertEqual(1, len(control.proposals))
        self.assertIn("mapping_list_fields", control.proposals[0].content)
        fields = control.proposals[0].content["mapping_list_fields"]
        self.assertIn("categories", fields)
        self.assertEqual({
            "added": [],
            "deleted": [json.loads(utils.as_json(category.log_json()))]
        }, fields["categories"])
        self.assertEqual(1, len(control.comments))

    def test_apply_empty_mapping_list(self):
        """Test apply mapping list proposal to empty."""
        with factories.single_commit():
            category = factories.ControlCategoryFactory()
            control = factories.ControlFactory()
            control.categories.append(category)
        control_id = control.id
        category_id = category.id
        with factories.single_commit():
            proposal = factories.ProposalFactory(
                instance=control,
                content={
                    "mapping_list_fields": {
                        "categories": {
                            "added": [],
                            "deleted": [
                                {
                                    "id": category_id,
                                    "type": "ControlCategory"
                                },
                            ]
                        }
                    }
                },
                agenda="agenda content")
        proposal_id = proposal.id
        with self.number_obj_revisions_for(control):
            self.apply_proposal(proposal, apply_reason="approved")
        proposal = all_models.Proposal.query.get(proposal_id)
        control = all_models.Control.query.get(control_id)
        self.assertEqual(proposal.STATES.APPLIED, proposal.status)
        control = all_models.Control.query.get(control_id)
        self.assertEqual([], control.categories)
        self.assertEqual(1, len(control.comments))

    def test_apply_mapping_list(self):
        """Test apply mapping list proposal."""
        with factories.single_commit():
            category = factories.ControlCategoryFactory()
            control = factories.ControlFactory()
        control_id = control.id
        category_id = category.id
        with factories.single_commit():
            proposal = factories.ProposalFactory(
                instance=control,
                content={
                    "mapping_list_fields": {
                        "categories": {
                            "deleted": [],
                            "added": [
                                {
                                    "id": category_id,
                                    "type": "ControlCategory"
                                },
                            ]
                        }
                    }
                },
                agenda="agenda content")
        proposal_id = proposal.id
        with self.number_obj_revisions_for(control):
            self.apply_proposal(proposal, apply_reason="approved")
        control = all_models.Control.query.get(control_id)
        proposal = all_models.Proposal.query.get(proposal_id)
        self.assertEqual(proposal.STATES.APPLIED, proposal.status)
        control = all_models.Control.query.get(control_id)
        self.assertEqual([all_models.ControlCategory.query.get(category_id)],
                         control.categories)
        self.assertEqual(1, len(control.comments))
        comment = control.comments[0]
        self.assertEqual(proposal, comment.initiator_instance)
