# coding: utf-8

# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Tests for /query api endpoint."""

import ddt
import sqlalchemy as sa

from ggrc.models import all_models
from ggrc.access_control import roleable

from integration.ggrc import TestCase
from integration.ggrc.api_helper import Api


@ddt.ddt
class TestQuery(TestCase):
  """Tests for /query api for ACR instance filtering."""

  def setUp(self):
    super(TestQuery, self).setUp()
    self.api = Api()
    self._full_reindex()

  @ddt.data(*[m for m in all_models.all_models
              if issubclass(m, roleable.Roleable)])
  def test_filter_acr_by_obj_type(self, model):
    """Test filter ACR by object type {0.__name__}."""
    query = all_models.AccessControlRole.query.filter(
        all_models.AccessControlRole.object_type == model.__name__,
        all_models.AccessControlRole.internal == sa.sql.expression.false(),
    )
    ids = set(i.id for i in query)
    query_request_data = [{
        u'fields': [],
        u'filters': {
            u'expression': {
                u'left': u'object_type',
                u'op': {u'name': u'='},
                u'right': model.__name__,
            }
        },
        u'limit': [0, 5],
        u'object_name': u'AccessControlRole',
        u'permissions': u'read',
        u'type': u'values',
    }]
    resp = self.api.send_request(
        self.api.client.post,
        data=query_request_data,
        api_link="/query")
    resp_data = resp.json[0]["AccessControlRole"]
    self.assertEqual(len(ids), resp_data["count"])
    self.assertEqual(ids, {i["id"] for i in resp_data["values"]})
