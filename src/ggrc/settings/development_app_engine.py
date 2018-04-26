# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

DEBUG = True
TESTING = False
PRODUCTION = False
HOST = '0.0.0.0'
SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:root@localhost/ggrcdev'
FULLTEXT_INDEXER = 'ggrc.fulltext.mysql.Indexer'
LOGIN_MANAGER = 'ggrc.login.appengine'
# SQLALCHEMY_ECHO = True
AUTOBUILD_ASSETS = False
ENABLE_JASMINE = False

APP_ENGINE = True
EXTERNAL_APP_USER = 'External App <external_app@example.com>'
