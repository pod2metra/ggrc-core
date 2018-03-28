# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Fulltext init indexer mudule"""

from ggrc.extensions import get_extension_instance


def get_indexer():
    """Get mysql indexer.

  This is a weird way of getting a MysqlIndexer "singleton". The indexer should
  be moved its own module and used without a class, and then this function
  should be removed.
  """
    return get_extension_instance("FULLTEXT_INDEXER",
                                  "ggrc.fulltext.mysql.MysqlIndexer")
