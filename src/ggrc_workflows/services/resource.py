# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Workflow specific Resources implementation."""

import datetime
from flask import current_app
from ggrc import db
from ggrc import utils
from ggrc.services.common import Resource


class CycleTaskResource(Resource):
  """Contains CycleTask's specific Resource implementation."""

  def patch(self):
    """PATCH operation handler."""
    src = self.request.json
    if self.request.mimetype != 'application/json':
      return current_app.make_response(
          ('Content-Type must be application/json', 415, []))
    with utils.benchmark("Do bulk update"):
      updated_ids, skipped_ids = self.model.bulk_update(src)
    with utils.benchmark("Commit"):
      db.session.commit()
    with utils.benchmark("Make response"):
      result = [{'status': 'updated', 'id': idx} for idx in updated_ids]
      result.extend([{'status': 'skipped', 'id': idx} for idx in skipped_ids])
      return self.json_success_response(result, datetime.datetime.now())
