# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

# pylint: disable=maybe-no-member, invalid-name

"""Test Issue import and updates."""

from collections import OrderedDict

from ggrc import models
from ggrc.converters import errors

from integration.ggrc.models import factories
from integration.ggrc import TestCase


class TestImportIssues(TestCase):
  """Basic Issue import tests."""

  def setUp(self):
    """Set up for Issue test cases."""
    super(TestImportIssues, self).setUp()
    self.client.get("/login")

  def test_basic_issue_import(self):
    """Test basic issue import."""
    audit = factories.AuditFactory()
    for i in range(2):
      response = self.import_data(OrderedDict([
          ("object_type", "Issue"),
          ("Code*", ""),
          ("Title*", "Test issue {}".format(i)),
          ("Owner*", "user@example.com"),
          ("audit", audit.slug),
      ]))
      self._check_csv_response(response, {})

    for issue in models.Issue.query:
      self.assertIsNotNone(
          models.Relationship.find_related(issue, audit),
          "Could not find relationship between: {} and {}".format(
              issue.slug, audit.slug)
      )

  def test_audit_change(self):
    audit = factories.AuditFactory()
    issue = factories.IssueFactory()
    response = self.import_data(OrderedDict([
        ("object_type", "Issue"),
        ("Code*", issue.slug),
        ("audit", audit.slug),
    ]))
    self._check_csv_response(response, {
        "Issue": {
            "row_warnings": {
                errors.UNMODIFIABLE_COLUMN.format(line=3, column_name="Audit")
            }
        }
    })
