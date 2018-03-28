# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""This module contains setter functions for different types of object
fields."""

from collections import defaultdict

from ggrc import utils, db
from ggrc.access_control.role import get_custom_roles_for
from ggrc.app import app

from ggrc.models import all_models
from integration.ggrc.models import factories

CAD_PERSON_TYPE = "Map:Person"
CAD_PERSON_TITLE = "CA_Person"

AC_ROLES = defaultdict(dict)
CADS = defaultdict(dict)


def init_globals(models):
    """Load all ACRs and CADs into memory from db"""
    with app.app_context():
        with factories.single_commit():
            for model in models:
                AC_ROLES[model] = {
                    name: id
                    for id, name in get_custom_roles_for(model).items()
                }

                CADS[model] = {
                    CAD_PERSON_TYPE:
                    factories.CustomAttributeDefinitionFactory(
                        title=CAD_PERSON_TITLE,
                        definition_type=utils.underscore_from_camelcase(model),
                        attribute_type=CAD_PERSON_TYPE,
                    ).id
                }


def generate_cad_attr_setter(cad_type):
    """Generate object setter function for CAV field"""

    def set_obj_attr(model, val):
        return {
            "custom_attribute_values_": [{
                "attribute_value":
                val.type,
                "attribute_object_id":
                val.id,
                "custom_attribute_id":
                CADS[model][cad_type],
            }]
        }

    return set_obj_attr


def generate_acr_attr_setter(role_name):
    """Generate object setter function for ACL related field"""

    def set_obj_attr(model, person):
        return {
            "access_control_list_": [{
                "ac_role_id": AC_ROLES[model][role_name],
                "person_id": person.id
            }]
        }

    return set_obj_attr


def generate_foreign_attr_setter(field):
    """Generate object setter function for foreign key field"""

    def set_obj_attr(_, val):
        return {field: val}

    return set_obj_attr


FIELD_SETTERS = {
    "modified_by": generate_foreign_attr_setter("modified_by"),
    CAD_PERSON_TITLE: generate_cad_attr_setter(CAD_PERSON_TYPE),
}
FIELD_SETTERS.update({
    role[0]: generate_acr_attr_setter(role[0])
    for role in db.session.query(all_models.AccessControlRole.name)
    .filter(all_models.AccessControlRole.non_editable).distinct()
})
