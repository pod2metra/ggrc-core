# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Sets up Flask app."""

import ggrc.login

from ggrc import db

from flask import Flask
from ggrc import settings

# pylint: disable=invalid-name
maintenance_app = Flask(
    'ggrc', instance_relative_config=True)  # noqa: valid constant name
maintenance_app.config.from_object(settings)
if "public_config" not in maintenance_app.config:
    maintenance_app.config.public_config = {}

for key in settings.exports:
    maintenance_app.config.public_config[key] = maintenance_app.config[key]

# Configure Flask-SQLAlchemy for app
db.app = maintenance_app
db.init_app(maintenance_app)
ggrc.login.init_app(maintenance_app)


def init_maintenance():
    """Initialize views for maintenance."""
    from ggrc.maintenance_views import maintenance  # noqa: need to import this to initialize


init_maintenance()
