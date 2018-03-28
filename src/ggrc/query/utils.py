# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Utils module for query generation."""

import sqlalchemy as sa


def get_type_select_column(model):
    """Get column name,taking into account polymorphic types."""
    mapper = model._sa_class_manager.mapper  # pylint: disable=protected-access
    if mapper.polymorphic_on is None:
        type_column = sa.literal(mapper.class_.__name__)
    else:
        # Handle polymorphic types with CASE
        type_column = sa.case(
            value=mapper.polymorphic_on,
            whens={
                val: m.class_.__name__
                for val, m in mapper.polymorphic_map.items()
            })
    return type_column
