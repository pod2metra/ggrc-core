# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add automappings table

Create Date: 2017-07-10 09:26:21.778041
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '2ada007df3ee'
down_revision = '51d5958779f1'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    # Rename automapping_id to parent_id
    op.drop_constraint(
        'relationships_automapping_parent',
        'relationships',
        type_='foreignkey')
    op.alter_column(
        'relationships',
        'automapping_id',
        existing_type=sa.Integer(),
        new_column_name='parent_id')
    op.create_foreign_key(
        "fk_relationships_parent_id",
        "relationships",
        "relationships", ["parent_id"], ["id"],
        ondelete='SET NULL')

    # Create the automappings table
    op.create_table('automappings',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('relationship_id', sa.Integer(), nullable=True),
                    sa.Column('source_id', sa.Integer(), nullable=False),
                    sa.Column(
                        'source_type', sa.String(length=250), nullable=False),
                    sa.Column('destination_id', sa.Integer(), nullable=False),
                    sa.Column(
                        'destination_type',
                        sa.String(length=250),
                        nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('modified_by_id', sa.Integer(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.Column('context_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['context_id'],
                        ['contexts.id'],
                    ), sa.PrimaryKeyConstraint('id'))
    op.create_index(
        'fk_automappings_contexts',
        'automappings', ['context_id'],
        unique=False)
    op.create_index(
        'ix_automappings_updated_at',
        'automappings', ['updated_at'],
        unique=False)
    op.add_column('relationships',
                  sa.Column('automapping_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_relationships_automapping_id",
        "relationships",
        "automappings", ["automapping_id"], ["id"],
        ondelete='CASCADE')


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    # Drop automappings table
    op.drop_index('ix_automappings_updated_at', table_name='automappings')
    op.drop_index('fk_automappings_contexts', table_name='automappings')
    op.drop_table('automappings')

    # Rename parent id to automapping id
    op.drop_constraint(
        'fk_relationship_automapping_id', 'relationships', type_='foreignkey')
    op.drop_constraint(
        'fk_relationship_parent_id', 'relationships', type_='foreignkey')
    op.drop_column('relationships', 'automapping_id')
    op.alter_column(
        'relationships',
        'parent_id',
        existing_type=sa.Integer(),
        new_column_name='automapping_id')
    op.create_foreign_key(
        "relationships_automapping_parent",
        "relationships",
        "relationships", ["automapping_id"], ["id"],
        ondelete='SET NULL')
