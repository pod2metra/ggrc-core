# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

from ggrc.models.all_models import register_model

from .risk import Risk
from .risk_object import RiskObject
from .threat import Threat

register_model(Risk)
register_model(RiskObject)
register_model(Threat)
