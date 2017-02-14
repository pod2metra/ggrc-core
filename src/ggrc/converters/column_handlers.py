# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
This module provides all column handlers for objects in the ggrc module.

If you want to add column handler you should decide is it handler default
or custom for current model.
If this handler is default than you will add it into _COLUMN_HANDLERS dict in
subdict by key "DEFAULT_HANDLERS_KEY"
If this handler is custom for current model you shuld add it in COLUMN_HANDLERS
dict by key "Model.__name__"

You may add column handlers in your extensions.
To make this you should add "EXTENSION_HANDLERS_ATTR" in __init__.py in your
extenstion.
It should be callable or dict.
If you want to add default handler you should add it in you
extension_handlers_dict by key "DEFAULT_HANDLERS_KEY"
If it is custom handler for current model, you should add it in
your "EXTENSION_HANDLERS_ATTR" dict by key "Model.__name__"

If you want to get hendler for your model
call function model_column_handlers with you model class as argument.

Example:

It returns all dict like:
    {
        "column_1"; HandlerClass1,
        "column_2": HandlerClass2,
        ...
    }
Thich contain handler for your Model.
"""
import itertools

from copy import deepcopy

from ggrc.converters.handlers import assessment_template
from ggrc.converters.handlers import boolean
from ggrc.converters.handlers import default_people
from ggrc.converters.handlers import handlers
from ggrc.converters.handlers import list_handlers
from ggrc.converters.handlers import related_person
from ggrc.converters.handlers import request
from ggrc.converters.handlers import template
from ggrc.converters.handlers import document
from ggrc.converters.handlers.custom_control_column_handler import (
    CustomControlSnapshotInstanceColumnHandler
)
from ggrc.converters.handlers.snapshot_instance_column_handler import (
    SnapshotInstanceColumnHandler
)
from ggrc.extensions import get_extension_modules
from ggrc.snapshotter import rules as snapshoted_rules
from ggrc import utils


_DEFAULT_COLUMN_HANDLERS_DICT = {
    "assertions": handlers.ControlAssertionColumnHandler,
    "assessment_template": assessment_template.AssessmentTemplateColumnHandler,
    "assignee": handlers.UserColumnHandler,
    "audit": handlers.AuditColumnHandler,
    "categories": handlers.ControlCategoryColumnHandler,
    "company": handlers.TextColumnHandler,
    "contact": handlers.UserColumnHandler,
    "default_assessors": default_people.DefaultPersonColumnHandler,
    "default_verifier": default_people.DefaultPersonColumnHandler,
    "delete": handlers.DeleteColumnHandler,
    "description": handlers.TextareaColumnHandler,
    "design": handlers.ConclusionColumnHandler,
    "document_evidence": document.DocumentEvidenceHandler,
    "document_url": document.DocumentUrlHandler,
    "documents": handlers.DocumentsColumnHandler,
    "due_on": handlers.DateColumnHandler,
    "email": handlers.EmailColumnHandler,
    "end_date": handlers.DateColumnHandler,
    "fraud_related": boolean.CheckboxColumnHandler,
    "is_enabled": boolean.CheckboxColumnHandler,
    "key_control": boolean.KeyControlColumnHandler,
    "kind": handlers.OptionColumnHandler,
    "link": handlers.TextColumnHandler,
    "means": handlers.OptionColumnHandler,
    "name": handlers.TextColumnHandler,
    "network_zone": handlers.OptionColumnHandler,
    "notes": handlers.TextareaColumnHandler,
    "operationally": handlers.ConclusionColumnHandler,
    "owners": handlers.OwnerColumnHandler,
    "principal_assessor": handlers.UserColumnHandler,
    "program": handlers.ProgramColumnHandler,
    "recipients": list_handlers.ValueListHandler,
    "reference_url": handlers.TextColumnHandler,
    "related_assessors": related_person.RelatedAssessorsColumnHandler,
    "related_assignees": related_person.RelatedAssigneesColumnHandler,
    "related_creators": related_person.RelatedCreatorsColumnHandler,
    "related_requesters": related_person.RelatedRequestersColumnHandler,
    "related_verifiers": related_person.RelatedVerifiersColumnHandler,
    "report_end_date": handlers.DateColumnHandler,
    "report_start_date": handlers.DateColumnHandler,
    "request": handlers.RequestColumnHandler,
    "request_audit": handlers.RequestAuditColumnHandler,
    "request_status": request.RequestStatusColumnHandler,
    "request_type": handlers.RequestTypeColumnHandler,
    "requested_on": handlers.DateColumnHandler,
    "secondary_assessor": handlers.UserColumnHandler,
    "secondary_contact": handlers.UserColumnHandler,
    "send_by_default": boolean.CheckboxColumnHandler,
    "slug": handlers.SlugColumnHandler,
    "start_date": handlers.DateColumnHandler,
    "status": handlers.StatusColumnHandler,
    "os_state": handlers.ExportOnlyColumnHandler,
    "template_custom_attributes": template.TemplateCaColumnHandler,
    "template_object_type": template.TemplateObjectColumnHandler,
    "test_plan": handlers.TextareaColumnHandler,
    "test_plan_procedure": boolean.CheckboxColumnHandler,
    "title": handlers.RequiredTextColumnHandler,
    "url": handlers.TextColumnHandler,
    "verify_frequency": handlers.OptionColumnHandler,

    # Mapping column handlers
    "__mapping__:person": handlers.PersonMappingColumnHandler,
    "__unmapping__:person": handlers.PersonUnmappingColumnHandler,
    "directive": handlers.SectionDirectiveColumnHandler,
}


DEFAULT_HANDLERS_KEY = "default"
EXTENSION_HANDLERS_ATTR = "contributed_column_handlers"


_COLUMN_HANDLERS = {
    DEFAULT_HANDLERS_KEY: _DEFAULT_COLUMN_HANDLERS_DICT,
    "Assessment": {
        "__mapping__:control": CustomControlSnapshotInstanceColumnHandler,
    },
    "Issue": {
        "__mapping__:control": CustomControlSnapshotInstanceColumnHandler,
    }
}


def populate_snapshoted_scope():
    mapping_rules = utils.get_mapping_rules()
    unmapping_rules = utils.get_unmapping_rules()

    def fielder(prefix, rules):
        for rule in rules:
            yield "{}:{}".format(prefix, utils.title_from_camelcase(rule))

    for model in snapshoted_rules.Types.scoped:
        mappings = mapping_rules.get(model, set())
        unmappings = unmapping_rules.get(model, set())
        mapping_fields = fielder("__mapping__", mappings)
        unmapping_fields = fielder("__unmapping__", unmappings)
        model_dict = _COLUMN_HANDLERS.get(model, {})
        for field in itertools.chain(mapping_fields, unmapping_fields):
            if field not in model_dict:
                model_dict[field] = SnapshotInstanceColumnHandler
        _COLUMN_HANDLERS[model] = model_dict


populate_snapshoted_scope()


def get_extensions_column_handlers():
  """Search through all enabled modules for their contributed column handlers.

  Returns:
    result_handlers (dict): dict of all extension handlers
  """
  result_handlers = deepcopy(_COLUMN_HANDLERS)
  for extension_module in get_extension_modules():
    extension_handlers = getattr(
        extension_module, EXTENSION_HANDLERS_ATTR, None)
    if callable(extension_handlers):
      extension_handlers = extension_handlers()
    if isinstance(extension_handlers, dict):
      for key, value_dict in extension_handlers.iteritems():
        result_handlers[key] = result_handlers.get(key, {})
        result_handlers[key].update(value_dict)
  return result_handlers


COLUMN_HANDLERS = get_extensions_column_handlers()


def model_column_handlers(cls):
  """Generates handlers for model class

  Attributes:
      cls (model class): Model class for which you are looking for handlers

  Returns:
      result_handlers (dict): dict of all handlers for current model class
                              the keys are column names
                              the values are handler classes
  """
  result_handlers = COLUMN_HANDLERS[DEFAULT_HANDLERS_KEY].copy()
  result_handlers.update(COLUMN_HANDLERS.get(cls.__name__, {}))
  return result_handlers
