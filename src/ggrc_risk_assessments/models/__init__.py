# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

from ggrc.models.all_models import register_model
from .risk_assessment import RiskAssessment

register_model(RiskAssessment)
