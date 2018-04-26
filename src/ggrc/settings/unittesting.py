# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

DEBUG = True
TESTING = True
LOGIN_DISABLED = False
PRODUCTION = False
HOST = '0.0.0.0'
SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:root@localhost/ggrcdevtest'
FULLTEXT_INDEXER = 'ggrc.fulltext.mysql.Indexer'
LOGIN_MANAGER = 'ggrc.login.noop'
# SQLALCHEMY_ECHO = True
