# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Create missing snapshot revisions.

Create Date: 2017-01-05 23:10:37.257161
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from ggrc.migrations.utils.snapshot_revisions import handle_objects

# revision identifiers, used by Alembic.
revision = '579239d161e1'
down_revision = '353e5f281799'


def upgrade():
    """Create missing revisions for snapshottable objects."""

    # copy pasted from ggrc.snapshoter.rules.Types.all
    snapshot_objects = sorted([
        "AccessGroup",
        "Clause",
        "Control",
        "DataAsset",
        "Facility",
        "Market",
        "Objective",
        "OrgGroup",
        "Product",
        "Section",
        "Vendor",
        "Policy",
        "Regulation",
        "Standard",
        "Contract",
        "System",
        "Process",
        "Risk",
        "Threat",
    ])

    handle_objects(snapshot_objects)


def downgrade():
    """Data correction migrations can not be downgraded."""
