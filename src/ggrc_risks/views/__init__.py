# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

from ggrc.app import app
from ggrc.login import login_required
from ggrc_risks.views import converters

from flask import render_template


def init_extra_views(app):
    pass
