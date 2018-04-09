# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Tests if error handling is done correctly"""

from integration.ggrc import TestCase


class TestErrorHandlers(TestCase):

  def test_non_flask_error_handling(self):
    response = self.import_file("not_a_csv.txt", dry_run=True)
    self.assertEqual(response["message"], "Invalid file type.")
