# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Main GGRC module"""
import time
from ggrc import bootstrap

INIT_TIME = time.time(), time.clock()
# pylint: disable=invalid-name
db = bootstrap.get_db()
