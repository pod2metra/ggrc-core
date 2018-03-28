# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
  Audit permission hooks

  The following permission hooks make sure archived audits are not editable
"""
from werkzeug.exceptions import Forbidden

from ggrc import db
from ggrc.models import all_models
from ggrc.services import signals


def init_hook():
    """Initializes audit permission hooks."""
    # pylint: disable=unused-variable
    @signals.Restful.model_put.connect_via(all_models.Audit)
    @signals.Restful.model_deleted.connect_via(all_models.Audit)
    def handle_audit_permission_put(sender, obj, src=None, service=None):
        """Make sure admins cannot delete/update archived audits"""
        # pylint: disable=unused-argument
        if obj.archived and not db.inspect(obj).get_history(
                'archived', False).has_changes():
            raise Forbidden()

    # pylint: disable=unused-variable
    @signals.Restful.model_deleted.connect_via(all_models.Assessment)
    @signals.Restful.model_deleted.connect_via(all_models.AssessmentTemplate)
    @signals.Restful.model_posted.connect_via(all_models.Assessment)
    @signals.Restful.model_posted.connect_via(all_models.AssessmentTemplate)
    @signals.Restful.model_put.connect_via(all_models.Assessment)
    @signals.Restful.model_put.connect_via(all_models.AssessmentTemplate)
    @signals.Restful.model_put.connect_via(all_models.Snapshot)
    def handle_archived_object(sender, obj=None, src=None, service=None):
        """Make sure admins cannot delete/update archived audits"""
        # pylint: disable=unused-argument
        if obj.archived:
            raise Forbidden()

    @signals.Restful.model_deleted.connect_via(all_models.Comment)
    @signals.Restful.model_deleted.connect_via(all_models.Document)
    @signals.Restful.model_deleted.connect_via(all_models.UserRole)
    @signals.Restful.model_posted.connect_via(all_models.Comment)
    @signals.Restful.model_posted.connect_via(all_models.Document)
    @signals.Restful.model_posted.connect_via(all_models.Snapshot)
    @signals.Restful.model_posted.connect_via(all_models.UserRole)
    def handle_archived_context(sender, obj=None, src=None, service=None):
        """Make sure admins cannot delete/update archived audits"""
        # pylint: disable=unused-argument
        if (hasattr(obj, 'context') and hasattr(obj.context, 'related_object')
                and getattr(obj.context.related_object, 'archived', False)):
            raise Forbidden()

    @signals.Restful.model_posted.connect_via(all_models.Relationship)
    @signals.Restful.model_deleted.connect_via(all_models.Relationship)
    def handle_archived_relationships(sender, obj=None, src=None,
                                      service=None):
        """Make sure users can not map objects to archived audits"""
        # pylint: disable=unused-argument
        if (getattr(obj, 'source_type', None) == 'Issue'
                or getattr(obj, 'destination_type', None) == 'Issue'):
            # Issues can be mapped even if audit is archived so skip the permission
            # check here
            return
        if (hasattr(obj, 'context') and hasattr(obj.context, 'related_object')
                and getattr(obj.context.related_object, 'archived', False)):
            raise Forbidden()
