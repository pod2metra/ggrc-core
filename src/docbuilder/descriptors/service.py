# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Service descriptor."""

from ggrc.models.reflection import AttributeInfo
from cached_property import cached_property

from docbuilder.descriptors.base import Descriptor
from docbuilder.descriptors.model import Model

MOCK_DATA = {
    "id": "1",
    "context": """{{ "id": 1, "type": "Context" }}""",
    "default_to_current_user": 'false',
    "delete": 'false',
    "mandatory": 'true',
    "read": 'true',
    "my_work": 'true',
    "name": '"Name"',
    'object_type': '"Object Type"',
    "tooltip": '"Tooltip information"',
    "update": 'false',
    "type": '"{object_type}"',
    "created_at": '"2015-08-14T14:24:43"',
    "updated_at": '"2015-08-14T14:24:43"',
    "modified_by": """{{ "id": 1, "type": "Person"}}""",
    "non_editable": "false",
    "access_control_list": """[{{}}]""",
    "custom_attribute_values": """[{{}}]""",
    "custom_attributes": """[{{}}]""",
    "custom_attribute_definitions": """[{{}}]""",
    "description": '"Object <b>description</b>"',
    "notes": "'Object <i>Notes</i>'",
    "object_people": "{{}}",
    "related_destinations": "[]",
    "related_sources": "[]",
    "slug": '"OBJECT-1"',
    "start_date": '"2015-08-14"',
    "status": '"Active"',
    "task_group_objects": "[]",
    "title": '"Object title"',
    "preconditions_failed": 'false',
    'archived': 'false',
    'assessment_type': 'Control',
    'assignees': '[]',
    'audit': '{{ "id": 1, "type": "Audit"}}',
    "design": '"Operationally"',
    "end_date": '"2015-08-14"',
    "finished_date": '"2015-08-14"',
    'send_by_default': "false",
    'verified': 'false',
    'verified_date': 'null',
    'audit_firm': '{{ "id": 1, "type": "OrgGroup"}}',
    'program': '{{ "id": 1, "type": "Program"}}',
}


class Service(Descriptor):
    """Service descriptor."""

    @classmethod
    def collect(cls):
        """Collects all application services."""
        from ggrc.services import all_services
        return all_services()

    @cached_property
    def name(self):
        """Service name."""
        return '%s -> %s' % (self.model.name, self.obj.name)

    @cached_property
    def table_singular(self):
        """Object's table_singualr forme."""
        return self.obj.model_class._inflector.table_singular

    @cached_property
    def json_value(self):
        """Json value"""

        def func(name):
            return MOCK_DATA.get(
                name, '""').format(object_type=self.obj.model_class.__name__)

        return func

    @cached_property
    def url(self):
        """Endpoint URL."""
        return '/api/%s' % self.obj.name

    @cached_property
    def attributes(self):
        """Endpoint attributes"""
        return AttributeInfo.gather_attr_dicts(self.obj.model_class,
                                               '_api_attrs')

    @cached_property
    def doc(self):
        """Doc-stirng of wrapped model class."""
        return self.model.doc

    @cached_property
    def model(self):
        """Descriptor of wrapped model class."""
        return Model(self.obj.model_class)

    @cached_property
    def readonly(self):
        """Is service read-only?"""
        return self.obj.service_class.__name__.startswith('ReadOnly')
