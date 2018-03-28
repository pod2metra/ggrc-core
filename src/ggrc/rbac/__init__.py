# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Basic permissions module."""

import sqlalchemy as sa


class SystemWideRoles(object):
    """List of system wide roles."""
    # pylint: disable=too-few-public-methods

    SUPERUSER = u"Superuser"
    ADMINISTRATOR = u"Administrator"
    EDITOR = u"Editor"
    READER = u"Reader"
    CREATOR = u"Creator"
    NO_ACCESS = u"No Access"

    admins = {SUPERUSER, ADMINISTRATOR}

    read_roles = {
        SUPERUSER,
        ADMINISTRATOR,
        EDITOR,
        READER,
    }

    update_roles = {
        SUPERUSER,
        ADMINISTRATOR,
        EDITOR,
    }


def context_query_filter(context_column, contexts):
    '''
  Intended for use by `model.query.filter(...)`
  If `contexts == None`, it's Admin (no filter), so return `True`
  Else, return the full query
  '''

    if contexts is None:
        # Admin context, no filter
        return sa.sql.true()
    else:
        filter_expr = None
        # Handle `NULL` context specially
        if None in contexts:
            filter_expr = context_column.is_(None)
            # We're modifying `contexts`, so copy
            contexts = set(contexts)
            contexts.remove(None)
        if filter_expr is None:
            # No valid contexts
            return sa.sql.false()
        return filter_expr
