# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Gdrive Models"""

from ggrc.models.all_models import register_model
from ggrc_gdrive_integration.models.object_event import ObjectEvent
from ggrc_gdrive_integration.models.object_file import ObjectFile

register_model(ObjectEvent)
register_model(ObjectFile)
