# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Remove contact columns

Create Date: 2017-10-11 07:35:46.436824
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision = "431dcf5c75af"
down_revision = "ee816a4379e"

COLUMNS = [
    {
        "table": "access_groups",
        "column_name": "contact_id",
        "fk_name": "access_groups_ibfk_1",
        "index_name": "fk_access_groups_contact"
    },
    {
        "table": "access_groups",
        "column_name": "secondary_contact_id",
        "fk_name": "access_groups_ibfk_3",
        "index_name": "fk_access_groups_secondary_contact"
    },
    {
        "table": "assessments",
        "column_name": "contact_id",
        "fk_name": "assessments_ibfk_1"
    },
    {
        "table": "assessments",
        "column_name": "secondary_contact_id",
        "fk_name": "assessments_ibfk_3"
    },
    {
        "table": "clauses",
        "column_name": "contact_id",
        "fk_name": "clauses_ibfk_1",
        "index_name": "contact_id"
    },
    {
        "table": "clauses",
        "column_name": "secondary_contact_id",
        "fk_name": "clauses_ibfk_4",
        "index_name": "secondary_contact_id"
    },
    {
        "table": "controls",
        "column_name": "contact_id",
        "index_name": "fk_controls_contact"
    },
    {
        "table": "controls",
        "column_name": "secondary_contact_id",
        "index_name": "fk_controls_secondary_contact"
    },
    {
        "table": "controls",
        "column_name": "principal_assessor_id",
        "index_name": "ix_controls_principal_assessor"
    },
    {
        "table": "controls",
        "column_name": "secondary_assessor_id",
        "index_name": "ix_controls_secondary_assessor"
    },
    {
        "table": "data_assets",
        "column_name": "contact_id",
        "index_name": "fk_data_assets_contact"
    },
    {
        "table": "data_assets",
        "column_name": "secondary_contact_id",
        "index_name": "fk_data_assets_secondary_contact"
    },
    {
        "table": "directives",
        "column_name": "contact_id",
        "index_name": "fk_directives_contact"
    },
    {
        "table": "directives",
        "column_name": "secondary_contact_id",
        "index_name": "fk_directives_secondary_contact"
    },
    {
        "table": "facilities",
        "column_name": "contact_id",
        "index_name": "fk_facilities_contact"
    },
    {
        "table": "facilities",
        "column_name": "secondary_contact_id",
        "index_name": "fk_facilities_secondary_contact"
    },
    {
        "table": "issues",
        "column_name": "contact_id",
        "fk_name": "issues_ibfk_1",
        "index_name": "contact_id"
    },
    {
        "table": "issues",
        "column_name": "secondary_contact_id",
        "fk_name": "issues_ibfk_3",
        "index_name": "secondary_contact_id"
    },
    {
        "table": "markets",
        "column_name": "contact_id",
        "index_name": "fk_markets_contact"
    },
    {
        "table": "markets",
        "column_name": "secondary_contact_id",
        "index_name": "fk_markets_secondary_contact"
    },
    {
        "table": "objectives",
        "column_name": "contact_id",
        "index_name": "fk_objectives_contact"
    },
    {
        "table": "objectives",
        "column_name": "secondary_contact_id",
        "index_name": "fk_objectives_secondary_contact"
    },
    {
        "table": "org_groups",
        "column_name": "contact_id",
        "index_name": "fk_org_groups_contact"
    },
    {
        "table": "org_groups",
        "column_name": "secondary_contact_id",
        "index_name": "fk_org_groups_secondary_contact"
    },
    {
        "table": "programs",
        "column_name": "contact_id",
        "index_name": "fk_programs_contact"
    },
    {
        "table": "programs",
        "column_name": "secondary_contact_id",
        "index_name": "fk_programs_secondary_contact"
    },
    {
        "table": "products",
        "column_name": "contact_id",
        "index_name": "fk_products_contact"
    },
    {
        "table": "products",
        "column_name": "secondary_contact_id",
        "index_name": "fk_products_secondary_contact"
    },
    {
        "table": "projects",
        "column_name": "contact_id",
        "index_name": "fk_projects_contact"
    },
    {
        "table": "projects",
        "column_name": "secondary_contact_id",
        "index_name": "fk_projects_secondary_contact"
    },
    {
        "table": "sections",
        "column_name": "contact_id",
        "index_name": "fk_sections_contact"
    },
    {
        "table": "sections",
        "column_name": "secondary_contact_id",
        "index_name": "fk_sections_secondary_contact"
    },
    {
        "table": "systems",
        "column_name": "contact_id",
        "index_name": "fk_systems_contact"
    },
    {
        "table": "systems",
        "column_name": "secondary_contact_id",
        "index_name": "fk_systems_secondary_contact"
    },
    {
        "table": "vendors",
        "column_name": "contact_id",
        "index_name": "fk_vendors_contact"
    },
    {
        "table": "vendors",
        "column_name": "secondary_contact_id",
        "index_name": "fk_vendors_secondary_contact"
    },
]


def drop_contact(table, column_name, fk_name=None, index_name=None):
    """Drop FK, index and then the column."""
    if fk_name:
        op.drop_constraint(fk_name, table, type_="foreignkey")
    if index_name:
        op.drop_index(index_name, table_name=table)
    op.drop_column(table, column_name)


def upgrade():
    """Remove columns for fields moved to ACL."""
    for item in COLUMNS:
        drop_contact(**item)


def create_contact(table, column_name, fk_name=None, index_name=None):
    """Create the column, FK and then index."""
    op.add_column(table,
                  sa.Column(
                      column_name,
                      mysql.INTEGER(display_width=11),
                      autoincrement=False,
                      nullable=True))
    if fk_name:
        op.create_foreign_key(fk_name, table, "people", [column_name], ["id"])
    if index_name:
        op.create_index(index_name, table, [column_name], unique=False)


def downgrade():
    """Revert columns removal"""
    for item in COLUMNS:
        create_contact(**item)
