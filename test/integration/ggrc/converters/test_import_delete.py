# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

from ggrc.models import all_models

from integration.ggrc import TestCase


class TestBasicCsvImport(TestCase):

  def setUp(self):
    super(TestBasicCsvImport, self).setUp()
    self.client.get("/login")

  def test_policy_basic_import(self):
    filename = "ca_setup_for_deletion.csv"
    revision_ids = [i.id for i in all_models.Revision.query]
    self.import_file(filename)
    filename = "ca_deletion.csv"
    response_data = self.import_file(filename)
    query = all_models.Revision.query.filter(
        all_models.Revision.id.in_(revision_ids),
    )
    self.assertEqual(len(revision_ids), len([i.id for i in query]))
    self.assertEqual(response_data[0]["deleted"], 2)
    self.assertEqual(response_data[0]["ignored"], 0)
