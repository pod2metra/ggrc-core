# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Services for create and manipulate objects via UI."""

from lib.constants import element
from lib.entities.entities_factory import (
    AssessmentTemplatesFactory, AssessmentsFactory, EntitiesFactory,
    ControlsFactory, AuditsFactory, IssuesFactory, ProgramsFactory)
from lib.page.widget.generic_widget import (
    Audits, AssessmentTemplates, Assessments, Controls, Issues, Programs)
from lib.page.widget.info_widget import AuditsInfoWidget
from lib.utils import selenium_utils, string_utils


class BaseWebUiService(object):
  """Base class for business layer's services objects."""
  def __init__(self, driver):
    self.driver = driver

  def create_list_objs(self, factory, list_scopes):
    """Create and return list of objects used entity factory and UI data
    (list of scopes UI text elements {"header": "item", ...} remapped to
    list of dicts {"attr": "value", ...}).
    Return list of created objects.
    """
    list_factory_objs = [
        factory.create_empty() for _ in xrange(len(list_scopes))]
    list_scopes_remapped = string_utils.remap_keys_for_list_dicts(
        dict_transformation_keys=self.ui_elements_to_obj_attrs(),
        list_dicts=list_scopes)
    return [
        EntitiesFactory.update_obj_attrs_values(
            obj=factory_obj, **scope_remapped) for
        scope_remapped, factory_obj in zip(list_scopes_remapped,
                                           list_factory_objs)]

  @staticmethod
  def ui_elements_to_obj_attrs():
    """Get transformation dictionary {"OLD KEY": "NEW KEY"}, where
    "OLD KEY" - UI elements correspond to "NEW KEY" - objects attributes.
    """
    fields = element.TransformationSetVisibleFields
    return {
        fields.TITLE.upper(): "title", fields.OWNER.upper(): "owner",
        fields.CODE.upper(): "code", fields.STATE.upper(): "state",
        fields.STATUS.upper(): "status",
        fields.VERIFIED.upper(): "is_verified",
        fields.LAST_UPDATED.upper(): "last_update",
        fields.AUDIT_LEAD.upper(): "audit_lead",
        fields.MANAGER.upper(): "manager",
        fields.PRIMARY_CONTACT.upper(): "primary_contact"
    }

  def create_obj_via_tree_view(self, widget_url, gen_widget, obj):
    """Navigate to widget URL, open creation modal from Tree View,
    fill data according to object attributes and create new object.
    """
    selenium_utils.open_url(self.driver, widget_url)
    objs_widget = gen_widget(self.driver).create()
    objs_widget.fill_minimal_data(obj.title, obj.code)
    objs_widget.save_and_close()

  def get_count_objs_from_tab(self, widget_url, gen_widget):
    """Navigate to widget URL, get count of objects from Tab navigation bar
    and return got count.
    """
    selenium_utils.open_url(self.driver, widget_url)
    return gen_widget(self.driver).member_count

  def get_list_scopes_from_tree_view(self, widget_url, gen_widget):
    """Navigate to widget URL, set visible fields and get list of objects
    scopes as dicts from header (keys) and items (values) that displayed
    in Tree View.
    """
    selenium_utils.open_url(self.driver, widget_url)
    return gen_widget(self.driver).get_list_objs_scopes()

  def get_scope_from_info_widget(self, info_page_url, info_widget):
    """Navigate to Info page URL and get object scope as dict with
    titles (keys) and entered_titles (values) that displayed in Info widget.
    """
    selenium_utils.open_url(self.driver, info_page_url)
    obj_info_page = info_widget(self.driver)
    return obj_info_page.get_obj_as_dict()

  def is_obj_editable_via_info_panel(self, widget_url, gen_widget, obj):
    """Navigate to widget URL, select object from Tree View by title and
    check via Info panel that object is editable.
    """
    selenium_utils.open_url(self.driver, widget_url)
    objs_widget = gen_widget(self.driver)
    return objs_widget.is_editable(obj_title=obj.title)

  def is_obj_page_exist_via_info_panel(self, widget_url, gen_widget, obj):
    """Navigate to widget URL, select object from Tree View by title and
    check via Info panel that object page is exist.
    """
    # pylint: disable=invalid-name
    selenium_utils.open_url(self.driver, widget_url)
    objs_widget = gen_widget(self.driver)
    return objs_widget.is_openable(obj_title=obj.title)


class AuditsService(BaseWebUiService):
  """Service for working with entity Audits entities."""

  def __init__(self, driver):
    super(AuditsService, self).__init__(driver)

  def generate_objs_via_tree_view(self, widget_url, gen_widget, obj,
                                  objs_under):
    """Navigate to widget URL, open Generation modal from Tree View,
    fill data according to object and objects under attributes,
    generate new object(s).
    """
    selenium_utils.open_url(self.driver, widget_url)
    objs_widget = gen_widget(self.driver).generate()
    objs_under_titles = [obj_under.title for obj_under in objs_under]
    objs_widget.fill_minimal_data(obj.title, objs_under_titles)
    objs_widget.generate_and_close()

  def update_obj_ver_via_info_panel(self, widget_url, gen_widget, obj):
    """Navigate to widget URL, select snapshotable object from Tree View
    by title and update object to latest version via Info panel.
    """
    selenium_utils.open_url(self.driver, widget_url)
    objs_widget = gen_widget(self.driver)
    objs_widget.update_ver(obj_title=obj.title)

  def clone_via_info_widget_get_obj(self, audit_obj):
    """Navigate to Info widget URL of Audit object and clone it including
    Assessment Templates via Info widget.
    Redirect to cloned Audit, get and return Audit object from Info widget.
    """
    audit_info_widget_url = Audits.URL_INFO.format(
        obj_url=audit_obj.url)
    selenium_utils.open_url(self.driver, audit_info_widget_url)
    audit_info_page = Audits.info_widget_cls(self.driver)
    (audit_info_page.
     open_info_3bbs().select_clone().confirm_clone(is_full=True))
    cloned_audit_obj = AuditsFactory().create_empty()
    cloned_audit_obj.url = self.driver.current_url
    actual_cloned_audit_obj = self.get_obj_from_info_widget(
        audit_obj=cloned_audit_obj)
    actual_cloned_audit_obj.url = cloned_audit_obj.url
    return actual_cloned_audit_obj

  def bulk_update_via_info_widget(self, audit_obj):
    """Navigate to Info widget URL of Audit object and bulk update objects to
    latest version.
    """
    audit_info_widget_url = Audits.URL_INFO.format(obj_url=audit_obj.url)
    selenium_utils.open_url(self.driver, audit_info_widget_url)
    audit_info_page = Audits.info_widget_cls(self.driver)
    (audit_info_page.
     open_info_3bbs().select_update_objs().confirm_update())

  def is_obj_updateble_via_info_panel(self, widget_url, gen_widget, obj):
    """Navigate to widget URL, select object from Tree View by title and
    check via Info panel that object is updateble.
    """
    selenium_utils.open_url(self.driver, widget_url)
    objs_widget = gen_widget(self.driver)
    return objs_widget.is_updateble(obj_title=obj.title)

  def get_obj_from_info_widget(self, audit_obj):
    """Get and return Audit object from Info widget."""
    scope = self.get_scope_from_info_widget(
        info_page_url=Audits.URL_INFO.format(obj_url=audit_obj.url),
        info_widget=AuditsInfoWidget)
    return self.create_list_objs(
        factory=AuditsFactory(), list_scopes=[scope])[0]


class AssessmentTemplatesService(BaseWebUiService):
  """Service for working with Assessment Templates entities."""
  def __init__(self, driver):
    super(AssessmentTemplatesService, self).__init__(driver)

  def create_via_tree_view(self, source_obj, asmt_tmpl_obj):
    """Create new Assessment Template object via Tree View."""
    self.create_obj_via_tree_view(
        widget_url=AssessmentTemplates.URL.format(
            source_obj_url=source_obj.url),
        gen_widget=AssessmentTemplates, obj=asmt_tmpl_obj)

  def get_count_from_tab(self, source_obj):
    """Get and return count of Assessment Templates objects from Tab
    navigation bar."""
    return self.get_count_objs_from_tab(
        widget_url=AssessmentTemplates.URL.format(
            source_obj_url=source_obj.url),
        gen_widget=AssessmentTemplates)

  def get_objs_from_tree_view(self, source_obj):
    """Get and return list of Assessment Templates objects from Tree View."""
    list_scopes = self.get_list_scopes_from_tree_view(
        widget_url=AssessmentTemplates.URL.format(
            source_obj_url=source_obj.url),
        gen_widget=AssessmentTemplates)
    return self.create_list_objs(
        factory=AssessmentTemplatesFactory(), list_scopes=list_scopes)


class AssessmentsService(BaseWebUiService):
  """Service for working with entity Assessments entities."""
  def __init__(self, driver):
    super(AssessmentsService, self).__init__(driver)

  def create_via_tree_view(self, source_obj, asmt_obj):
    """Create new Assessment object via Tree View."""
    self.create_obj_via_tree_view(
        widget_url=Assessments.URL.format(
            source_obj_url=source_obj.url), gen_widget=Assessments,
        obj=asmt_obj)

  def generate_via_tree_view(self, source_obj, asmt_tmpl_obj, objs_under_asmt):
    """Generate new Assessment(s) object(s) via Tree View."""
    AuditsService(self.driver).generate_objs_via_tree_view(
        widget_url=Assessments.URL.format(
            source_obj_url=source_obj.url),
        gen_widget=Assessments, obj=asmt_tmpl_obj,
        objs_under=objs_under_asmt)

  def get_count_from_tab(self, source_obj):
    """Get and return count of Assessments objects from Tab Navigation bar."""
    return self.get_count_objs_from_tab(
        widget_url=Assessments.URL.format(
            source_obj_url=source_obj.url),
        gen_widget=Assessments)

  def get_objs_from_tree_view(self, source_obj):
    """Get and return list of Assessments objects from Tree View."""
    list_scopes = self.get_list_scopes_from_tree_view(
        widget_url=Assessments.URL.format(
            source_obj_url=source_obj.url),
        gen_widget=Assessments)
    return self.create_list_objs(
        factory=AssessmentsFactory(), list_scopes=list_scopes)


class ControlsService(BaseWebUiService):
  """Service for working with Controls entities."""
  def __init__(self, driver):
    super(ControlsService, self).__init__(driver)

  def update_ver_via_info_panel(self, source_obj, control_obj):
    """Update version of Control object via Info panel from Tree View."""
    AuditsService(self.driver).update_obj_ver_via_info_panel(
        widget_url=Controls.URL.format(source_obj_url=source_obj.url),
        gen_widget=Controls, obj=control_obj)

  def get_count_from_tab(self, source_obj):
    """Get and return count of Controls objects from Tab navigation bar."""
    return self.get_count_objs_from_tab(
        widget_url=Controls.URL.format(source_obj_url=source_obj.url),
        gen_widget=Controls)

  def get_objs_from_tree_view(self, source_obj):
    """Get and return list of Controls objects from Tree View."""
    list_scopes = self.get_list_scopes_from_tree_view(
        widget_url=Controls.URL.format(source_obj_url=source_obj.url),
        gen_widget=Controls)
    return self.create_list_objs(
        factory=ControlsFactory(), list_scopes=list_scopes)

  def is_editable_via_info_panel(self, source_obj, control_obj):
    """Check that Control object is editable via Info panel from Tree View.
    If editable then return 'True' if no editable then return 'False'."""
    return self.is_obj_editable_via_info_panel(
        widget_url=Controls.URL.format(source_obj_url=source_obj.url),
        gen_widget=Controls, obj=control_obj)

  def is_updateble_via_info_panel(self, source_obj, control_obj):
    """Check that Control object is updateble via Info panel from Tree View.
    If updateble then return 'True' if no updateble then return 'False'."""
    return AuditsService(self.driver).is_obj_updateble_via_info_panel(
        widget_url=Controls.URL.format(source_obj_url=source_obj.url),
        gen_widget=Controls, obj=control_obj)

  def is_openable_via_info_panel(self, source_obj, control_obj):
    """Check that Control object is openable via Info panel from Tree View.
    If openable then return 'True' if no openable then return 'False'."""
    return self.is_obj_page_exist_via_info_panel(
        widget_url=Controls.URL.format(source_obj_url=source_obj.url),
        gen_widget=Controls, obj=control_obj)


class IssuesService(BaseWebUiService):
  """Service for working with Issues entities."""

  def __init__(self, driver):
    super(IssuesService, self).__init__(driver)

  def get_count_from_tab(self, source_obj):
    """Get and return count of Issues objects from Tab navigation bar."""
    return self.get_count_objs_from_tab(
        widget_url=Issues.URL.format(source_obj_url=source_obj.url),
        gen_widget=Issues)

  def get_objs_from_tree_view(self, source_obj):
    """Get and return list of Issues objects from Tree View."""
    list_scopes = self.get_list_scopes_from_tree_view(
        widget_url=Issues.URL.format(source_obj_url=source_obj.url),
        gen_widget=Issues)
    return self.create_list_objs(
        factory=IssuesFactory(), list_scopes=list_scopes)


class ProgramsService(BaseWebUiService):
  """Service for working with Programs entities."""

  def __init__(self, driver):
    super(ProgramsService, self).__init__(driver)

  def get_count_from_tab(self, source_obj):
    """Get and return count of Programs objects from Tab navigation bar."""
    return self.get_count_objs_from_tab(
        widget_url=Programs.URL.format(source_obj_url=source_obj.url),
        gen_widget=Programs)

  def get_objs_from_tree_view(self, source_obj):
    """Get and return list of Programs objects from Tree View."""
    list_scopes = self.get_list_scopes_from_tree_view(
        widget_url=Programs.URL.format(source_obj_url=source_obj.url),
        gen_widget=Programs)
    return self.create_list_objs(
        factory=ProgramsFactory(), list_scopes=list_scopes)
