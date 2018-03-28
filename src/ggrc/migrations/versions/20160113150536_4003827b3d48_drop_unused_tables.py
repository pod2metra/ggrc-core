# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Drop unused tables

Revision ID: 4003827b3d48
Revises: 5410607088f9
Create Date: 2016-01-13 15:05:36.008456

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '4003827b3d48'
down_revision = '5410607088f9'


def upgrade():
    tables = [
        "object_sections", "control_sections", "objective_controls",
        "program_controls", "directive_controls", "control_controls",
        "calendar_entries", "object_objectives", "object_controls",
        "section_objectives", "program_directives", "directive_sections"
    ]
    for table in tables:
        try:
            op.drop_table(table)
        except sa.exc.OperationalError as operr:
            # Ignores error in case relationship_types table no longer exists
            error_code, _ = operr.orig.args  # error_code, message
            if error_code != 1051:
                raise operr


def downgrade():
    op.create_table(
        'directive_sections',
        sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
        sa.Column(
            'directive_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'section_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column('status', mysql.VARCHAR(length=250), nullable=True),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column(
            'modified_by_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column(
            'context_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_default_charset=u'utf8',
        mysql_engine=u'InnoDB')
    op.create_table(
        'program_directives',
        sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
        sa.Column(
            'modified_by_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column(
            'program_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'directive_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'context_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.Column('status', mysql.VARCHAR(length=250), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_default_charset=u'utf8',
        mysql_engine=u'InnoDB')
    op.create_table(
        'section_objectives',
        sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
        sa.Column(
            'modified_by_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column(
            'section_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'objective_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'context_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.Column('status', mysql.VARCHAR(length=250), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_default_charset=u'utf8',
        mysql_engine=u'InnoDB')
    op.create_table(
        'object_controls',
        sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
        sa.Column(
            'modified_by_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column('start_date', sa.DATE(), nullable=True),
        sa.Column('end_date', sa.DATE(), nullable=True),
        sa.Column('role', mysql.VARCHAR(length=250), nullable=True),
        sa.Column('notes', mysql.TEXT(), nullable=True),
        sa.Column(
            'control_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'controllable_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'controllable_type', mysql.VARCHAR(length=250), nullable=False),
        sa.Column(
            'context_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.Column('status', mysql.VARCHAR(length=250), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_default_charset=u'utf8',
        mysql_engine=u'InnoDB')
    op.create_table(
        'object_objectives',
        sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
        sa.Column(
            'modified_by_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column('start_date', sa.DATE(), nullable=True),
        sa.Column('end_date', sa.DATE(), nullable=True),
        sa.Column('role', mysql.VARCHAR(length=250), nullable=True),
        sa.Column('notes', mysql.TEXT(), nullable=True),
        sa.Column(
            'objective_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'objectiveable_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'objectiveable_type', mysql.VARCHAR(length=250), nullable=False),
        sa.Column(
            'context_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.Column('status', mysql.VARCHAR(length=250), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_default_charset=u'utf8',
        mysql_engine=u'InnoDB')
    op.create_table(
        'calendar_entries',
        sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
        sa.Column('name', mysql.VARCHAR(length=250), nullable=True),
        sa.Column('calendar_id', mysql.VARCHAR(length=250), nullable=True),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column(
            'modified_by_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column(
            'context_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.Column(
            'owner_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.ForeignKeyConstraint(
            ['context_id'], [u'contexts.id'], name=u'calendar_entries_ibfk_1'),
        sa.ForeignKeyConstraint(
            ['owner_id'], [u'people.id'], name=u'calendar_entries_ibfk_2'),
        sa.PrimaryKeyConstraint('id'),
        mysql_default_charset=u'utf8',
        mysql_engine=u'InnoDB')
    op.create_table(
        'control_controls',
        sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
        sa.Column(
            'modified_by_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column(
            'control_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'implemented_control_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'context_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.Column('status', mysql.VARCHAR(length=250), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_default_charset=u'utf8',
        mysql_engine=u'InnoDB')
    op.create_table(
        'directive_controls',
        sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
        sa.Column(
            'modified_by_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column(
            'directive_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'control_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'context_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.Column('status', mysql.VARCHAR(length=250), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_default_charset=u'utf8',
        mysql_engine=u'InnoDB')
    op.create_table(
        'program_controls',
        sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
        sa.Column(
            'modified_by_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column(
            'context_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.Column(
            'program_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'control_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column('status', mysql.VARCHAR(length=250), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_default_charset=u'utf8',
        mysql_engine=u'InnoDB')
    op.create_table(
        'objective_controls',
        sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
        sa.Column(
            'modified_by_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column(
            'objective_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'control_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'context_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.Column('status', mysql.VARCHAR(length=250), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_default_charset=u'utf8',
        mysql_engine=u'InnoDB')
    op.create_table(
        'control_sections',
        sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
        sa.Column(
            'modified_by_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column(
            'control_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'section_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'context_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.Column('status', mysql.VARCHAR(length=250), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_default_charset=u'utf8',
        mysql_engine=u'InnoDB')
    op.create_table(
        'object_sections',
        sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
        sa.Column(
            'modified_by_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column('start_date', sa.DATE(), nullable=True),
        sa.Column('end_date', sa.DATE(), nullable=True),
        sa.Column('role', mysql.VARCHAR(length=250), nullable=True),
        sa.Column('notes', mysql.TEXT(), nullable=True),
        sa.Column(
            'section_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'sectionable_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'sectionable_type', mysql.VARCHAR(length=250), nullable=False),
        sa.Column(
            'context_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.Column('status', mysql.VARCHAR(length=250), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_default_charset=u'utf8',
        mysql_engine=u'InnoDB')
