# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name
"""
Fix tracking columns.

These helpers is used by the following migrations:

* ggrc.migrations.verisions.20160728120017_29c8b9c5d34b;
* ggrc_basic_permissions.migrations.verisions.20160728142641_4e105fc39b25;
* ggrc_gdrive_integration.migrations.verisions.20160804095642_395186a2d8;
* ggrc_risk_assessments.migrations.verisions.20160804101106_4d4b04a5b9c6;
* ggrc_risks.migrations.verisions.20160804095405_3d2acc8a4425;
* ggrc_workflows.migrations.verisions.20160728142921_4cb78ab9a321.

"""

import sqlalchemy as sa
from alembic import op

tables = {
    "ggrc": [
        "access_groups",
        "assessment_templates",
        "assessments",
        "audit_objects",
        "audits",
        "background_tasks",
        "categories",
        "categorizations",
        "clauses",
        "comments",
        "contexts",
        "controls",
        "custom_attribute_definitions",
        "custom_attribute_values",
        "data_assets",
        "directives",
        "documents",
        "events",
        "facilities",
        "helps",
        "issues",
        "markets",
        "meetings",
        "notification_configs",
        "notification_types",
        "notifications",
        "object_owners",
        "object_people",
        "objectives",
        "options",
        "org_groups",
        "people",
        "products",
        "programs",
        "projects",
        "relationships",
        "requests",
        "revisions",
        "sections",
        "systems",
        "vendors",
    ],
    "ggrc_gdrive_integration": [
        "object_events",
        "object_files",
        "object_folders",
    ],
    "ggrc_basic_permissions": [
        "context_implications",
        "contexts",
        "roles",
        "user_roles",
    ],
    "ggrc_risks": [
        "risks",
        "risk_objects",
        "threats",
    ],
    "ggrc_risk_assessments": [
        "risk_assessments",
    ],
    "ggrc_workflows": [
        "cycle_task_entries",
        "cycle_task_group_object_tasks",
        "cycle_task_group_objects",
        "cycle_task_groups",
        "cycles",
        "notification_types",
        "task_group_objects",
        "task_group_tasks",
        "task_groups",
        "workflow_people",
        "workflows",
    ],
}


def upgrade_tables(module):
    """Updgrade tables from given module."""
    for table in tables[module]:
        op.execute("""
        UPDATE %s
        SET
            created_at = IF(
                created_at,
                created_at,
                IF(updated_at, updated_at, now())
            ),
            updated_at = IF(
                updated_at,
                updated_at,
                IF(created_at, created_at, now())
            )
        WHERE created_at IS NULL OR updated_at IS NULL
    """ % table)
        op.alter_column(table, "created_at", type_=sa.DateTime, nullable=False)
        op.alter_column(table, "updated_at", type_=sa.DateTime, nullable=False)


def downgrade_tables(module):
    """Downgrade tables from given module."""
    for table in tables[module]:
        op.alter_column(table, "created_at", type_=sa.DateTime, nullable=True)
        op.alter_column(table, "updated_at", type_=sa.DateTime, nullable=True)
