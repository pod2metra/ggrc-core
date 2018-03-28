# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Assessments Workflow smoke tests."""
# pylint: disable=no-self-use
# pylint: disable=invalid-name
# pylint: disable=unused-argument
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments

import pytest

from lib import base
from lib.constants import messages, element, value_aliases as alias
from lib.constants.element import AssessmentStates
from lib.entities import entities_factory
from lib.entities.entities_factory import (CustomAttributeDefinitionsFactory,
                                           PeopleFactory)
from lib.entities.entity import Representation
from lib.service import rest_service, webui_service
from lib.utils.filter_utils import FilterUtils
from lib.utils.string_utils import StringMethods


class TestAssessmentsWorkflow(base.Test):
    """Tests for Assessments Workflow functionality."""
    info_service = rest_service.ObjectsInfoService()

    @pytest.mark.smoke_tests
    def test_add_comment_to_asmt_via_info_panel(self, new_program_rest,
                                                new_audit_rest,
                                                new_assessment_rest, selenium):
        """Check via UI of possibility to correctly add comment to Assessment via
    Info Panel.
    Preconditions:
    - Program created via REST API.
    - Audit created under Program via REST API.
    - Assessment created under Audit via REST API.
    Test parameters: None
    """
        expected_asmt_comments = [entities_factory.CommentsFactory().create()]
        expected_asmt = new_assessment_rest
        asmts_ui_service = webui_service.AssessmentsService(selenium)
        asmt_comments_panel = asmts_ui_service.add_comments(
            src_obj=new_audit_rest,
            obj=expected_asmt,
            comment_objs=expected_asmt_comments)
        assert asmt_comments_panel.is_input_empty is True
        # 'expected_asmt_comments': created_at (None) *factory
        expected_asmt_comments = [
            expected_comment.update_attrs(
                created_at=self.info_service.get_comment_obj(
                    paren_obj=expected_asmt,
                    comment_description=expected_comment.description)
                .created_at).repr_ui()
            for expected_comment in expected_asmt_comments
        ]
        # 'expected_asmt': updated_at (outdated)
        expected_asmt.update_attrs(
            updated_at=self.info_service.get_obj(obj=expected_asmt).updated_at,
            comments=expected_asmt_comments,
            status=AssessmentStates.IN_PROGRESS).repr_ui()
        actual_asmt = asmts_ui_service.get_obj_from_info_page(
            obj=expected_asmt)
        # 'actual_asmt': audit (None)
        self.general_equal_assert(expected_asmt, actual_asmt, "audit",
                                  "comments")
        self.xfail_equal_assert(expected_asmt, actual_asmt,
                                "Issue in app GGRC-3094", "comments")

    @pytest.mark.smoke_tests
    def test_asmt_logs(self, new_program_rest, new_audit_rest,
                       new_assessment_rest, selenium):
        """Test for validation of Assessment log pane.
    Acceptance criteria:
      1) 3 log items at the log pane
      2) all items return 'True' for all attrs.
    """
        log_items_validation = webui_service.AssessmentsService(
            selenium).get_log_pane_validation_result(obj=new_assessment_rest)
        log_validation_results = [
            all(item_result.values()) for item_result in log_items_validation
        ]
        assert (
            [True] * 2) == log_validation_results, str(log_items_validation)

    @pytest.mark.smoke_tests
    def test_asmt_related_asmts(self, new_program_rest, new_control_rest,
                                map_new_program_rest_to_new_control_rest,
                                new_audit_rest, new_assessments_rest,
                                selenium):
        """Test for checking Related Assessments. Map two Assessments to one
    snapshot of control. And check second Assessment contains in "Related
    Assessments" Tab of first Assessment. 3 Titles will be compared:
    Assessment, Audit of Assessment, generic Control.
    """
        expected_titles = [(new_assessments_rest[1].title,
                            new_control_rest.title, new_audit_rest.title)]
        asmts_ui_service = webui_service.AssessmentsService(selenium)
        asmts_ui_service.map_objs_via_tree_view_item(
            src_obj=new_audit_rest, dest_objs=[new_control_rest])
        related_asmts_objs_titles = (asmts_ui_service.get_related_asmts_titles(
            obj=new_assessments_rest[0]))
        assert expected_titles == related_asmts_objs_titles

    @pytest.mark.smoke_tests
    def test_raise_issue(self, new_program_rest, new_audit_rest,
                         new_assessment_rest, selenium):
        """Test for checking raising Issues in Related Issues Tab. Open
    Related Issues tab on Assessments Info page. Raise Issue with pre-defined
    attributes via "raise issue" button. Compare expected Issue title and
    actual issue_titles.
    """
        expected_issue = (entities_factory.IssuesFactory().create().repr_ui())
        asmts_ui_service = webui_service.AssessmentsService(selenium)
        asmts_ui_service.raise_issue(new_assessment_rest, expected_issue)
        related_issues_titles = asmts_ui_service.get_related_issues_titles(
            obj=new_assessment_rest)
        assert related_issues_titles == [expected_issue.title]

    @pytest.mark.smoke_tests
    @pytest.mark.parametrize(
        ("dynamic_objects_w_factory_params", "action", "expected_final_state",
         "expected_verified"),
        [(("new_assessment_rest", {
            "status": AssessmentStates.NOT_STARTED
        }), "edit_obj_via_edit_modal_from_info_page",
          AssessmentStates.NOT_STARTED, False),
         (("new_assessment_rest", {
             "status": AssessmentStates.NOT_STARTED,
             "verifiers": [PeopleFactory().default_user]
         }), "edit_obj_via_edit_modal_from_info_page",
          AssessmentStates.NOT_STARTED, False),
         (("new_assessment_rest", {
             "status": AssessmentStates.IN_PROGRESS
         }), "edit_obj_via_edit_modal_from_info_page",
          AssessmentStates.IN_PROGRESS, False),
         (("new_assessment_rest", {
             "status": AssessmentStates.IN_PROGRESS,
             "verifiers": [PeopleFactory().default_user]
         }), "edit_obj_via_edit_modal_from_info_page",
          AssessmentStates.IN_PROGRESS, False),
         (("new_assessment_rest", {
             "status": AssessmentStates.COMPLETED
         }), "edit_obj_via_edit_modal_from_info_page",
          AssessmentStates.IN_PROGRESS, False),
         (("new_assessment_rest", {
             "status": AssessmentStates.COMPLETED,
             "verifiers": [PeopleFactory().default_user]
         }), "edit_obj_via_edit_modal_from_info_page",
          AssessmentStates.IN_PROGRESS, False),
         (("new_assessment_rest", {
             "status": AssessmentStates.NOT_STARTED
         }), "complete_assessment", AssessmentStates.COMPLETED, False),
         (("new_assessment_rest", {
             "status": AssessmentStates.NOT_STARTED,
             "verifiers": [PeopleFactory().default_user]
         }), "complete_assessment", AssessmentStates.READY_FOR_REVIEW, False),
         (("new_assessment_rest", {
             "status": AssessmentStates.IN_PROGRESS
         }), "complete_assessment", AssessmentStates.COMPLETED, False),
         (("new_assessment_rest", {
             "status": AssessmentStates.IN_PROGRESS,
             "verifiers": [PeopleFactory().default_user]
         }), "complete_assessment", AssessmentStates.READY_FOR_REVIEW, False),
         (("new_assessment_rest", {
             "status": AssessmentStates.NOT_STARTED,
             "verifiers": [PeopleFactory().default_user]
         }), "verify_assessment", AssessmentStates.COMPLETED, True),
         (("new_assessment_rest", {
             "status": AssessmentStates.NOT_STARTED,
             "verifiers": [PeopleFactory().default_user]
         }), "reject_assessment", AssessmentStates.REWORK_NEEDED, False)],
        ids=[
            "Edit asmt's title w'o verifier 'Not Started' - 'Not Started'",
            "Edit asmt's title w' verifier 'Not Started' - 'Not Started'",
            "Edit asmt's title w'o verifier 'In Progress' - 'In Progress'",
            "Edit asmt's title w' verifier 'In Progress' - 'In Progress'",
            "Edit asmt's title w'o verifier 'Completed' - 'In Progress'",
            "Edit asmt's title w' verifier 'Completed' - 'In Progress'",
            "Complete asmt w'o verifier 'Not Started' - 'Completed'",
            "Complete asmt w' verifier 'Not Started' - 'In Review'",
            "Complete asmt w'o verifier 'In Progress' - 'Completed'",
            "Complete asmt w' verifier 'In Progress' - 'In Review'",
            "Verify asmt w' verifier 'In Review' - 'Completed'",
            "Reject asmt w' verifier 'In Review' - 'Rework Needed'"
        ],
        indirect=["dynamic_objects_w_factory_params"])
    def test_check_asmt_state_change(self, new_program_rest, new_audit_rest,
                                     dynamic_objects_w_factory_params, action,
                                     expected_final_state, expected_verified,
                                     selenium):
        """Check Assessment workflow status change to correct state.
    Preconditions:
    - Program created via REST API.
    - Audit created under Program via REST API.
    - Assessment created and updated under Audit via REST API.
    """
        expected_asmt = dynamic_objects_w_factory_params
        asmts_ui_service = webui_service.AssessmentsService(selenium)
        # UI part of preparing pre-requirements (due to REST doesn't allow it)
        if action in ("verify_assessment", "reject_assessment"):
            getattr(asmts_ui_service, "complete_assessment")(expected_asmt)
        getattr(asmts_ui_service, action)(expected_asmt)
        # 'expected_asmt': updated_at (outdated)
        expected_asmt.update_attrs(
            title=(element.AssessmentInfoWidget.TITLE_EDITED_PART +
                   expected_asmt.title
                   if "edit" in action else expected_asmt.title),
            status=expected_final_state.title(),
            verified=expected_verified,
            updated_at=self.info_service.get_obj(
                obj=expected_asmt).updated_at).repr_ui()
        actual_asmt = asmts_ui_service.get_obj_from_info_page(expected_asmt)
        # 'actual_asmt': audit (None)
        self.general_equal_assert(expected_asmt, actual_asmt, "audit")

    @pytest.mark.smoke_tests
    @pytest.mark.parametrize("operator", [alias.EQUAL_OP, alias.CONTAINS_OP])
    def test_asmts_gcas_filtering(self, new_program_rest, new_audit_rest,
                                  new_cas_for_assessments_rest,
                                  new_assessments_rest, operator, selenium):
        """Test for checking filtering of Assessment by Global Custom Attributes
    in audit scope.
    Preconditions:
    - Program created via REST API.
    - Audit created via REST API.
    - Global Custom Attributes for Assessment created via REST API.
    - Assessments created via REST API.
    """
        custom_attr_values = (CustomAttributeDefinitionsFactory(
        ).generate_ca_values(list_ca_def_objs=new_cas_for_assessments_rest))
        checkbox_id = Representation.filter_objs_by_attrs(
            objs=new_cas_for_assessments_rest,
            attribute_type=element.AdminWidgetCustomAttributes.CHECKBOX).id
        expected_asmt = new_assessments_rest[0]
        asmts_rest_service = rest_service.AssessmentsService()
        asmts_rest_service.update_obj(
            obj=expected_asmt, custom_attributes=custom_attr_values)
        asmts_rest_service.update_obj(
            obj=new_assessments_rest[1],
            custom_attributes={
                checkbox_id: not custom_attr_values[checkbox_id]
            })
        self._check_assessments_filtration(expected_asmt, custom_attr_values,
                                           operator, new_audit_rest, selenium)

    @pytest.mark.smoke_tests
    @pytest.mark.parametrize("operator", [alias.EQUAL_OP])
    def test_asmts_lcas_filtering(
            self, new_program_rest, new_controls_rest,
            map_new_program_rest_to_new_controls_rest, new_audit_rest,
            new_assessment_template_with_cas_rest,
            new_assessments_from_template_rest, operator, selenium):
        """Test for checking filtering of Assessment by Local Custom Attributes
    in audit scope.
    Preconditions:
    - Program created via REST API.
    - Controls created via REST API and mapped to program.
    - Audit created via REST API.
    - Assessment template with LCA created via REST API.
    - Assessments for assessment template created via REST API.
    """

        def set_values_for_assessment(assessment, only_checkbox,
                                      checkbox_value):
            """Set LCA values for assessment"""
            custom_attr_definitions = [
                CustomAttributeDefinitionsFactory().create(**definition)
                for definition in assessment.cads_from_template()
            ]
            checkbox_id = Representation.filter_objs_by_attrs(
                objs=custom_attr_definitions,
                attribute_type=element.AdminWidgetCustomAttributes.CHECKBOX).id
            if only_checkbox:
                attr_values = {}
            else:
                attr_values = CustomAttributeDefinitionsFactory(
                ).generate_ca_values(list_ca_def_objs=custom_attr_definitions)
                attr_values[checkbox_id] = checkbox_value
            rest_service.AssessmentsService().update_obj(
                obj=assessment, custom_attributes=attr_values)
            return attr_values

        unchecked_asmt = new_assessments_from_template_rest[0]
        checked_asmt = new_assessments_from_template_rest[1]

        set_values_for_assessment(
            unchecked_asmt, only_checkbox=True, checkbox_value=False)
        set_attr_values = set_values_for_assessment(
            checked_asmt, only_checkbox=False, checkbox_value=True)

        self._check_assessments_filtration(checked_asmt, set_attr_values,
                                           operator, new_audit_rest, selenium)

    @staticmethod
    def _check_assessments_filtration(assessment, attr_values, operator, audit,
                                      selenium):
        """Check that filtration of assessments works."""
        filter_exprs = FilterUtils().get_filter_exprs_by_cas(
            assessment.custom_attribute_definitions, attr_values, operator)
        assessment = Representation.extract_objs_wo_excluded_attrs(
            [assessment.repr_ui()],
            *(Representation.tree_view_attrs_to_exclude +
              ("audit", "assessment_type", "modified_by")))[0]
        expected_results = [{
            "filter": filter_expr,
            "objs": [assessment]
        } for filter_expr in filter_exprs]
        actual_results = []
        for filter_expr in filter_exprs:
            result = {
                "filter":
                filter_expr,
                "objs":
                webui_service.AssessmentsService(selenium)
                .filter_and_get_list_objs_from_tree_view(audit, filter_expr)
            }
            actual_results.append(result)
        error_message = messages.AssertionMessages.format_err_msg_equal([{
            exp_res["filter"]: [exp_obj.title for exp_obj in exp_res["objs"]]
        } for exp_res in expected_results], [
            {
                act_res["filter"]:
                [act_obj.title for act_obj in act_res["objs"]]
            } for act_res in actual_results
        ]) + messages.AssertionMessages.format_err_msg_equal(
            StringMethods.convert_list_elements_to_list(
                [exp_res["objs"] for exp_res in expected_results]),
            StringMethods.convert_list_elements_to_list(
                [act_res["objs"] for act_res in actual_results]))
        assert expected_results == actual_results, error_message

    @pytest.mark.smoke_tests
    @pytest.mark.parametrize(
        "dynamic_objects, dynamic_relationships",
        [("new_objective_rest", "map_new_program_rest_to_new_objective_rest"),
         ("new_control_rest", "map_new_program_rest_to_new_control_rest")],
        indirect=True)
    def test_map_snapsots_to_asmt_via_edit_modal(
            self, new_program_rest, dynamic_objects, dynamic_relationships,
            new_audit_rest, new_assessment_rest, selenium):
        """Check Assessment can be mapped with snapshot via Modal Edit
    on Assessments Info Page. Additional check existing of mapped obj Titles
    on Modal Edit.
    Preconditions:
    - Program, dynamic_objects created via REST API.
    - dynamic_objects mapped to Program via REST API.
    - Audit created under Program via REST API.
    - Assessment created under audit via REST API.
    Test parameters:
    - 'dynamic_objects'.
    - 'dynamic_relationships'.
    """
        expected_asmt = (
            new_assessment_rest.update_attrs(mapped_objects=[dynamic_objects]))
        expected_titles = [dynamic_objects.title]
        asmts_ui_service = webui_service.AssessmentsService(selenium)
        actual_titles = (
            asmts_ui_service.map_objs_and_get_mapped_titles_from_edit_modal(
                expected_asmt, expected_asmt.mapped_objects))
        assert expected_titles == actual_titles
        # 'expected_asmt': updated_at (outdated)
        expected_asmt.update_attrs(
            updated_at=self.info_service.get_obj(
                obj=expected_asmt).updated_at).repr_ui()
        actual_asmt = asmts_ui_service.get_obj_from_info_page(expected_asmt)
        # 'actual_asmts': audit (None)
        self.general_equal_assert(expected_asmt, actual_asmt, "audit")
