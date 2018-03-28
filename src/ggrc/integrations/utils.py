# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Module provides various utils for Issue tracker integration service."""

import logging

from sqlalchemy.sql import expression

from ggrc.integrations import issues, integrations_errors
from ggrc.models import IssuetrackerIssue

logger = logging.getLogger(__name__)


def sync_issue_tracker_statuses():
    """Synchronize issue tracker ticket statuses with the Assessment statuses.

  Check for Assessments which are in sync with issue tracker issues and update
  their statuses in accordance to the corresponding Assessments if differ.
  """
    issue_objects = IssuetrackerIssue.query.filter(
        IssuetrackerIssue.object_type == 'Assessment',
        IssuetrackerIssue.enabled == expression.true(),
        IssuetrackerIssue.issue_id.isnot(None),
    ).order_by(IssuetrackerIssue.object_id).all()
    for iti in issue_objects:
        asmt = iti.issue_tracked_obj
        if not asmt:
            logger.error(
                "The Assessment corresponding to the Issue Tracker Issue ID=%d "
                "does not exist.", iti.issue_id)
            continue
        status_value = issues.STATUSES.get(asmt.status)
        if status_value:
            issue_params = {
                'status': status_value,
                'type': iti.issue_type,
                'priority': iti.issue_priority,
                'severity': iti.issue_severity,
            }
        else:
            logger.error(
                "Inexistent Issue Tracker status for assessment ID=%d "
                "with status: %s.", asmt.id, status_value)
        try:
            issues.Client().update_issue(iti.issue_id, issue_params)
        except integrations_errors.Error as error:
            logger.error('Unable to update IssueTracker issue status ID=%s '
                         'for assessment ID=%d: %s', iti.issue_id, asmt.id,
                         error)
