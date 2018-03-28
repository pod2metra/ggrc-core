# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
""" Module for handling import and export of all risk models """

from ggrc_risks import models

IMPORTABLE = {
    "risk": models.Risk,
    "threat": models.Threat,
}
