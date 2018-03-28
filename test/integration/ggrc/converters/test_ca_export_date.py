# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Tests export of objects with date CA and import files back."""
from StringIO import StringIO
from mock import patch

from ggrc.models import all_models
from integration.ggrc import TestCase, read_imported_file

from integration.ggrc.models import factories


class TestCustomAttributeExportDate(TestCase):
    """Tests date format for CA with date type in exported file.

  Test suite for checking date format of CA in the exported
  file of an object, e.g. Control.
  """

    def setUp(self):
        """Set up for CA export date test cases."""
        super(TestCustomAttributeExportDate, self).setUp()
        self.client.get("/login")

        with factories.single_commit():
            cad1 = factories.CustomAttributeDefinitionFactory(
                title="Test Date",
                definition_type="control",
                attribute_type="Date")
            cad2 = factories.CustomAttributeDefinitionFactory(
                title="Test Invalid Date",
                definition_type="control",
                attribute_type="Date")

            control = factories.ControlFactory()

            factories.CustomAttributeValueFactory(
                attributable=control,
                custom_attribute=cad1,
                attribute_value=u"2018-01-19")

            factories.CustomAttributeValueFactory(
                attributable=control,
                custom_attribute=cad2,
                attribute_value=u"Test Value")

            admin = factories.PersonFactory(
                email="test@example.com", name='test')

            acr_id = all_models.AccessControlRole.query.filter_by(
                object_type=control.type, name="Admin").first().id

            factories.AccessControlListFactory(
                person=admin, object=control, ac_role_id=acr_id)

        self.search_request = [{
            "object_name": "Control",
            "filters": {
                "expression": {},
            },
            "fields": "all"
        }]

    def test_ca_export_date(self):
        """Export control with date CA."""
        exported_data = self.export_parsed_csv(self.search_request)["Control"]

        self.assertTrue(len(exported_data) == 1)

        data = exported_data[0]
        self.assertEqual(data["Test Date"], u"01/19/2018")
        self.assertEqual(data["Test Invalid Date"], u"")

    @patch("ggrc.gdrive.file_actions.get_gdrive_file", new=read_imported_file)
    def test_import_exported(self):
        """Import previously exported file"""
        exported_data = self.export_csv(self.search_request).data

        _file = StringIO(exported_data)

        data = {"file": (_file, "test.csv")}
        response = self.send_import_request(data)

        expected_errors = {}

        self._check_csv_response(response, expected_errors)
