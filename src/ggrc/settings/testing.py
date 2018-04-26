# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

import os

DEBUG = True
TESTING = True
LOGIN_DISABLED = False
PRODUCTION = False
HOST = '0.0.0.0'
SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:root@{}/ggrcdevtest'.format(
    os.environ.get('GGRC_DATABASE_HOST', 'localhost')
)
FULLTEXT_INDEXER = 'ggrc.fulltext.mysql.Indexer'
LOGIN_MANAGER = 'ggrc.login.noop'
# SQLALCHEMY_ECHO = True
MEMCACHE_MECHANISM = False
EXTERNAL_APP_USER = 'External App <external_app@example.com>'
ENABLE_RELEASE_NOTES = False
