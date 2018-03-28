# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Test /suggest REST API
"""

import ddt
import mock

from ggrc.integrations.client import PersonClient
from integration.ggrc import TestCase
from integration.ggrc.api_helper import Api


@ddt.ddt
class TestSuggest(TestCase):
    """Test /suggest REST API"""

    def setUp(self):
        super(TestSuggest, self).setUp()
        self.api = Api()

    @ddt.data((' prefix ', ['prefix']), ('prefix', ['prefix']),
              ('Jhon Snow', ['Jhon', 'Snow']),
              ('  Jhon   Snow  ', ['Jhon', 'Snow']))
    @ddt.unpack
    @mock.patch('ggrc.settings.INTEGRATION_SERVICE_URL', new='endpoint')
    @mock.patch('ggrc.settings.AUTHORIZED_DOMAIN', new='example.com')
    def test_sugggest(self, prefix, expected):
        """Test suggest."""
        query = '/people/suggest?prefix={}'.format(prefix)
        with mock.patch.multiple(
                PersonClient,
                _post=mock.MagicMock(
                    return_value={
                        'persons': [
                            {
                                'uri': '1912',
                                'username': 'aturing',
                                'personNumber': '1912',
                                'firstName': 'Alan',
                                'lastName': 'Turing'
                            },
                            {
                                'uri': '1791',
                                'username': 'cbabbage',
                                'personNumber': '1791',
                                'firstName': 'Charles',
                                'lastName': 'Babbage'
                            },
                        ]
                    })):
            response = self.api.client.get(query)
            self.assert200(response)
            self.assertEqual(response.json, [
                {
                    'name': 'Alan Turing',
                    'email': 'aturing@example.com'
                },
                {
                    'name': 'Charles Babbage',
                    'email': 'cbabbage@example.com'
                },
            ])
            # pylint: disable=protected-access
            PersonClient._post.assert_called_once_with(
                '/api/persons:suggest', payload={
                    'tokens': expected,
                })

    @ddt.data('', '  ')
    @mock.patch('ggrc.settings.INTEGRATION_SERVICE_URL', new='endpoint')
    @mock.patch('ggrc.settings.AUTHORIZED_DOMAIN', new='example.com')
    def test_empty_prefix(self, prefix):
        """Test suggest for empty prefix."""
        query = '/people/suggest?prefix={}'.format(prefix)
        with mock.patch.multiple(
                PersonClient,
                _post=mock.MagicMock(return_value={'persons': []})):
            response = self.api.client.get(query)
            self.assert200(response)
            self.assertEqual(response.json, [])
            # pylint: disable=protected-access
            PersonClient._post.assert_not_called()
