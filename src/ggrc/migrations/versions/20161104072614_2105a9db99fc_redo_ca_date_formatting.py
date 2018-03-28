# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Redo CA date formatting.

This migration is a partial duplicate of 53206b20c12b. The formatting is
performed again because not every source of invalid dates was fixed prior to
53206b20c12b.

Create Date: 2016-11-04 07:26:14.880610
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

from ggrc.migrations.utils import fix_dates

# revision identifiers, used by Alembic.
revision = '2105a9db99fc'
down_revision = '1db61b597d2d'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    connection = op.get_bind()

    # only format MM/DD/YYYY with variations
    fix_dates.fix_single_digit_month(connection)
    fix_dates.fix_single_digit_day(connection)
    fix_dates.american_date_to_iso(connection)


def downgrade():
    """Do nothing."""
    # no formating required, every formatting downgrade is done in 53206b20c12b
    pass
