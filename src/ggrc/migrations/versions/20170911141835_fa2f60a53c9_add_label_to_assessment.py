# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
add label to assessment

Create Date: 2017-09-11 14:18:35.792388
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'fa2f60a53c9'
down_revision = '3e7c7f3d9308'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.add_column('assessments',
                  sa.Column(
                      'label',
                      sa.Enum(u'Needs Discussion', u'Needs Rework',
                              u'Followup', u'Auditor pulls evidence'),
                      nullable=True))
    op.create_index(
        'fk_assessments_label', 'assessments', ['label'], unique=False)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_index('fk_assessments_label', table_name='assessments')
    op.drop_column('assessments', 'label')
