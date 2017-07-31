# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""This module contains logic to handle '/query' endpoint."""

import time
from wsgiref.handlers import format_date_time

from flask import request
from flask import current_app
from werkzeug.exceptions import BadRequest

from ggrc.query.exceptions import BadQueryException
from ggrc.query.default_handler import DefaultHandler
from ggrc.login import login_required
from ggrc.models.inflector import get_model
from ggrc.services.common import etag
from ggrc.utils import as_json


def build_collection_representation(model, description):
  """Enclose collection description into a type-describing block."""
  # pylint: disable=protected-access
  collection = {
      model.__name__: description,
  }
  return collection


def json_success_response(response_object, last_modified=None, status=200):
  """Build a 200-response with metadata headers."""
  headers = [
      ('Etag', etag(response_object)),
      ('Content-Type', 'application/json'),
  ]
  if last_modified is not None:
    headers.append(('Last-Modified', http_timestamp(last_modified)))

  return current_app.make_response(
      (as_json(response_object), status, headers),
  )


def http_timestamp(timestamp):
  return format_date_time(time.mktime(timestamp.utctimetuple()))


def get_objects_by_query():
  """Return objects corresponding to a POST'ed query list."""
  query = request.json

  query_handler = DefaultHandler(query)
  results = query_handler.get_results()

  last_modified_list = [result["last_modified"] for result in results
                        if result["last_modified"]]
  last_modified = max(last_modified_list) if last_modified_list else None
  collections = []
  collection_fields = ["ids", "values", "count", "total"]

  for result in results:
    if last_modified is None:
      last_modified = result["last_modified"]
    elif result["last_modified"] is not None:
      last_modified = max(last_modified, result["last_modified"])

    model = get_model(result["object_name"])

    collection = build_collection_representation(
        model,
        {
            field: result[field] for field in collection_fields
            if field in result
        }
    )
    collections.append(collection)

  return json_success_response(collections, last_modified)


def init_query_views(app):
  # pylint: disable=unused-variable
  @app.route('/query', methods=['POST'])
  @login_required
  def query_objects():
    """Advanced object collection queries view."""
    try:
      return get_objects_by_query()
    except (NotImplementedError, BadQueryException) as exc:
      raise BadRequest(exc.message)
