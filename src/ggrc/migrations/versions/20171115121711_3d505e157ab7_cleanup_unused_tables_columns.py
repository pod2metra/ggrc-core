# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Cleanup unused tables and columns

Create Date: 2017-11-15 12:17:11.987633
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision = '3d505e157ab7'
down_revision = '14f51dd9affb'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    # pylint: disable=R0915
    op.drop_table('object_owners')
    op.drop_table('object_documents')
    op.drop_table('relationship_attrs')

    op.drop_column('access_groups', 'url')
    op.drop_column('access_groups', 'reference_url')

    op.drop_column('assessments', 'url')
    op.drop_column('assessments', 'reference_url')

    op.drop_column('audits', 'url')
    op.drop_column('audits', 'reference_url')

    op.drop_column('clauses', 'url')
    op.drop_column('clauses', 'reference_url')

    op.drop_column('controls', 'url')
    op.drop_column('controls', 'reference_url')

    op.drop_column('data_assets', 'url')
    op.drop_column('data_assets', 'reference_url')

    op.drop_column('directives', 'url')
    op.drop_column('directives', 'reference_url')

    op.drop_column('facilities', 'url')
    op.drop_column('facilities', 'reference_url')

    op.drop_column('issues', 'url')
    op.drop_column('issues', 'reference_url')

    op.drop_column('markets', 'url')
    op.drop_column('markets', 'reference_url')

    op.drop_column('objectives', 'url')
    op.drop_column('objectives', 'reference_url')

    op.drop_column('org_groups', 'url')
    op.drop_column('org_groups', 'reference_url')

    op.drop_column('products', 'url')
    op.drop_column('products', 'reference_url')

    op.drop_column('programs', 'url')
    op.drop_column('programs', 'reference_url')

    op.drop_column('projects', 'url')
    op.drop_column('projects', 'reference_url')

    op.drop_column('sections', 'end_date')
    op.drop_column('sections', 'url')
    op.drop_column('sections', 'reference_url')
    op.drop_column('sections', 'start_date')

    op.drop_column('systems', 'url')
    op.drop_column('systems', 'reference_url')

    op.drop_column('vendors', 'url')
    op.drop_column('vendors', 'reference_url')


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    # pylint: disable=R0915
    op.add_column('vendors',
                  sa.Column(
                      'reference_url',
                      mysql.VARCHAR(length=250),
                      nullable=True))
    op.add_column('vendors',
                  sa.Column('url', mysql.VARCHAR(length=250), nullable=True))

    op.add_column('systems',
                  sa.Column(
                      'reference_url',
                      mysql.VARCHAR(length=250),
                      nullable=True))
    op.add_column('systems',
                  sa.Column('url', mysql.VARCHAR(length=250), nullable=True))

    op.add_column('sections', sa.Column(
        'start_date', sa.DATE(), nullable=True))
    op.add_column('sections',
                  sa.Column(
                      'reference_url',
                      mysql.VARCHAR(length=250),
                      nullable=True))
    op.add_column('sections',
                  sa.Column('url', mysql.VARCHAR(length=250), nullable=True))
    op.add_column('sections', sa.Column('end_date', sa.DATE(), nullable=True))

    op.add_column('projects',
                  sa.Column(
                      'reference_url',
                      mysql.VARCHAR(length=250),
                      nullable=True))
    op.add_column('projects',
                  sa.Column('url', mysql.VARCHAR(length=250), nullable=True))

    op.add_column('programs',
                  sa.Column(
                      'reference_url',
                      mysql.VARCHAR(length=250),
                      nullable=True))
    op.add_column('programs',
                  sa.Column('url', mysql.VARCHAR(length=250), nullable=True))

    op.add_column('products',
                  sa.Column(
                      'reference_url',
                      mysql.VARCHAR(length=250),
                      nullable=True))
    op.add_column('products',
                  sa.Column('url', mysql.VARCHAR(length=250), nullable=True))

    op.add_column('org_groups',
                  sa.Column(
                      'reference_url',
                      mysql.VARCHAR(length=250),
                      nullable=True))
    op.add_column('org_groups',
                  sa.Column('url', mysql.VARCHAR(length=250), nullable=True))

    op.add_column('objectives',
                  sa.Column(
                      'reference_url',
                      mysql.VARCHAR(length=250),
                      nullable=True))
    op.add_column('objectives',
                  sa.Column('url', mysql.VARCHAR(length=250), nullable=True))

    op.add_column('markets',
                  sa.Column(
                      'reference_url',
                      mysql.VARCHAR(length=250),
                      nullable=True))
    op.add_column('markets',
                  sa.Column('url', mysql.VARCHAR(length=250), nullable=True))

    op.add_column('issues',
                  sa.Column(
                      'reference_url',
                      mysql.VARCHAR(length=250),
                      nullable=True))
    op.add_column('issues',
                  sa.Column('url', mysql.VARCHAR(length=250), nullable=True))

    op.add_column('facilities',
                  sa.Column(
                      'reference_url',
                      mysql.VARCHAR(length=250),
                      nullable=True))
    op.add_column('facilities',
                  sa.Column('url', mysql.VARCHAR(length=250), nullable=True))

    op.add_column('directives',
                  sa.Column(
                      'reference_url',
                      mysql.VARCHAR(length=250),
                      nullable=True))
    op.add_column('directives',
                  sa.Column('url', mysql.VARCHAR(length=250), nullable=True))

    op.add_column('data_assets',
                  sa.Column(
                      'reference_url',
                      mysql.VARCHAR(length=250),
                      nullable=True))
    op.add_column('data_assets',
                  sa.Column('url', mysql.VARCHAR(length=250), nullable=True))

    op.add_column('controls',
                  sa.Column(
                      'reference_url',
                      mysql.VARCHAR(length=250),
                      nullable=True))
    op.add_column('controls',
                  sa.Column('url', mysql.VARCHAR(length=250), nullable=True))

    op.add_column('clauses',
                  sa.Column(
                      'reference_url',
                      mysql.VARCHAR(length=250),
                      nullable=True))
    op.add_column('clauses',
                  sa.Column('url', mysql.VARCHAR(length=250), nullable=True))

    op.add_column('audits',
                  sa.Column(
                      'reference_url',
                      mysql.VARCHAR(length=250),
                      nullable=True))
    op.add_column('audits',
                  sa.Column('url', mysql.VARCHAR(length=250), nullable=True))

    op.add_column('assessments',
                  sa.Column(
                      'reference_url',
                      mysql.VARCHAR(length=250),
                      nullable=True))
    op.add_column('assessments',
                  sa.Column('url', mysql.VARCHAR(length=250), nullable=True))

    op.add_column('access_groups',
                  sa.Column(
                      'reference_url',
                      mysql.VARCHAR(length=250),
                      nullable=True))
    op.add_column('access_groups',
                  sa.Column('url', mysql.VARCHAR(length=250), nullable=True))

    op.create_table(
        'relationship_attrs',
        sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
        sa.Column(
            'relationship_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column('attr_name', mysql.VARCHAR(length=250), nullable=False),
        sa.Column('attr_value', mysql.VARCHAR(length=250), nullable=False),
        sa.ForeignKeyConstraint(
            ['relationship_id'], [u'relationships.id'],
            name=u'relationship_attrs_ibfk_1',
            ondelete=u'CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        mysql_default_charset=u'utf8',
        mysql_engine=u'InnoDB')
    op.create_table(
        'object_documents',
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
            'document_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'documentable_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'documentable_type', mysql.VARCHAR(length=250), nullable=False),
        sa.Column(
            'context_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.ForeignKeyConstraint(
            ['context_id'], [u'contexts.id'],
            name=u'fk_object_documents_contexts'),
        sa.ForeignKeyConstraint(
            ['document_id'], [u'documents.id'],
            name=u'object_documents_ibfk_1'),
        sa.PrimaryKeyConstraint('id'),
        mysql_default_charset=u'utf8',
        mysql_engine=u'InnoDB')
    op.create_table(
        'object_owners',
        sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
        sa.Column(
            'person_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'ownable_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False),
        sa.Column('ownable_type', mysql.VARCHAR(length=250), nullable=False),
        sa.Column(
            'modified_by_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.Column('created_at', mysql.DATETIME(), nullable=False),
        sa.Column('updated_at', mysql.DATETIME(), nullable=False),
        sa.Column(
            'context_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True),
        sa.ForeignKeyConstraint(
            ['context_id'], [u'contexts.id'], name=u'object_owners_ibfk_2'),
        sa.ForeignKeyConstraint(
            ['person_id'], [u'people.id'], name=u'object_owners_ibfk_1'),
        sa.PrimaryKeyConstraint('id'),
        mysql_default_charset=u'utf8',
        mysql_engine=u'InnoDB')
