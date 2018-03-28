# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Suggest persons by prefix"""

import json

from flask import current_app
from flask import request
from sqlalchemy import or_
from sqlalchemy.orm import load_only

from ggrc.integrations import client
from ggrc import settings
from ggrc.models import all_models


def mock_suggest():
    """Mocks the url request for local development
     Called when INTEGRATION_SERVICE_URL=mock"""
    tokens = request.args.get("prefix", "")
    results = all_models.Person.query\
        .filter(or_(
            all_models.Person.name.ilike('%{}%'.format(tokens)),
            all_models.Person.email.ilike('%{}%'.format(tokens))))\
        .options(load_only("name", "email"))\
        .order_by(all_models.Person.email)[:20]
    return make_suggest_result([{
        "firstName": result.name,
        "lastName": "",
        "username": result.email.split('@')[0]
    } for result in results])


def suggest():
    """Suggest persons by prefix"""
    if not settings.INTEGRATION_SERVICE_URL:
        return make_suggest_result([])

    if settings.INTEGRATION_SERVICE_URL == 'mock':
        return mock_suggest()

    tokens = request.args.get("prefix", "").split()
    if tokens:
        person_client = client.PersonClient()
        entries = person_client.suggest_persons(tokens)
        return make_suggest_result(entries)
    return make_suggest_result([])


def make_suggest_result(entries):
    """Build suggest response"""
    domain = getattr(settings, "AUTHORIZED_DOMAIN", "")
    return current_app.make_response((
        json.dumps([{
            "name": "%s %s" % (entry["firstName"], entry["lastName"]),
            "email": "%s@%s" % (entry["username"], domain),
        } for entry in entries]),
        200,
        [('Content-Type', 'application/json')],
    ))
