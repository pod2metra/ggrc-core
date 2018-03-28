# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add Snapshot model

Create Date: 2016-07-28 14:09:21.338385
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "2a5a39600741"
down_revision = "1f5c3e0025da"


def upgrade():
    """Add snapshots table"""
    op.create_table("snapshots", sa.Column("id", sa.Integer(), nullable=False),
                    sa.Column("parent_id", sa.Integer(), nullable=False),
                    sa.Column(
                        "parent_type", sa.String(length=250), nullable=False),
                    sa.Column("child_id", sa.Integer(), nullable=False),
                    sa.Column(
                        "child_type", sa.String(length=250), nullable=False),
                    sa.Column("revision_id", sa.Integer(), nullable=False),
                    sa.Column("context_id", sa.Integer(), nullable=True),
                    sa.Column("created_at", sa.DateTime(), nullable=False),
                    sa.Column("updated_at", sa.DateTime(), nullable=False),
                    sa.Column("modified_by_id", sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint("id"),
                    sa.ForeignKeyConstraint(["revision_id"], ["revisions.id"]))

    op.create_index(
        "ix_snapshots_parent",
        "snapshots", ["parent_type", "parent_id"],
        unique=False)
    op.create_index(
        "ix_snapshots_child",
        "snapshots", ["child_type", "child_id"],
        unique=False)
    op.create_index(
        "fk_snapshots_contexts", "snapshots", ["context_id"], unique=False)
    op.create_index(
        "ix_snapshots_updated_at", "snapshots", ["updated_at"], unique=False)
    op.create_unique_constraint(
        None, "snapshots",
        ["parent_type", "parent_id", "child_type", "child_id"])


def downgrade():
    """Drop snapshots table and audit's FF for snapshots"""
    op.drop_table("snapshots")
