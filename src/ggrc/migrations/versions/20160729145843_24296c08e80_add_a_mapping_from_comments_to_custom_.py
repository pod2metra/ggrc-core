# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Add a mapping from comments to custom attribute value revisions and custom
attribute definitions

Create Date: 2016-07-29 14:58:43.735355
"""

# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '24296c08e80'
down_revision = '29c8b9c5d34b'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.add_column('comments',
                  sa.Column('revision_id', sa.Integer(), nullable=True))
    op.add_column('comments',
                  sa.Column(
                      'custom_attribute_definition_id',
                      sa.Integer(),
                      nullable=True))
    op.create_foreign_key(
        'fk_comments_revisions',
        'comments',
        'revisions', ['revision_id'], ['id'],
        ondelete='SET NULL')
    op.create_foreign_key(
        'fk_comments_custom_attribute_definitions',
        'comments',
        'custom_attribute_definitions', ['custom_attribute_definition_id'],
        ['id'],
        ondelete='SET NULL')


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_constraint('fk_comments_custom_attribute_definitions', 'comments',
                       'foreignkey')
    op.drop_constraint('fk_comments_revisions', 'comments', 'foreignkey')
    op.drop_column('comments', 'custom_attribute_definition_id')
    op.drop_column('comments', 'revision_id')
