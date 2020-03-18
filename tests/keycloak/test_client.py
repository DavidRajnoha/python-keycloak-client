from unittest import TestCase

import mock

from keycloak.client import KeycloakClient


class KeycloakClientTestCase(TestCase):

    def setUp(self):
        self.headers = {'initial': 'header'}
        self.session = mock.MagicMock()
        self.session.headers.update(self.headers)
        self.server_url = 'https://example.com'

        self.client = KeycloakClient(server_url=self.server_url,
                                     session=self.session)

    def test_default_client_logger_name(self):
        """
        Case: Session get requested
        Expected: Session object get returned and the same one if called for
                  the second time
        """

        self.assertEqual(self.client.logger.name, 'KeycloakClient')

    def test_session(self):
        """
        Case: Session get requested
        Expected: Session object get returned and the same one if called for
                  the second time
        """
        session = self.client.session

        self.assertEqual(session, self.client.session)

    def test_get_full_url(self):
        """
        Case: retrieve a valid url
        Expected: The path get added to the base url or to the given url
        """

        self.assertEqual(self.client.get_full_url('/some/path'),
                         'https://example.com/some/path')

        self.assertEqual(self.client.get_full_url('/some/path',
                                                  'https://another_url.com'),
                         'https://another_url.com/some/path')

    def test_post(self):
        """
        Case: A POST request get executed
        Expected: The correct parameters get given to the request library
        """
        self.client._handle_response = mock.MagicMock()
        response = self.client.post(url='https://example.com/test',
                                    data={'some': 'data'},
                                    headers={'some': 'header'},
                                    extra='param')

        self.session.post.assert_called_once_with(
            'https://example.com/test',
            data={'some': 'data'},
            headers={'some': 'header'},
            params={'extra': 'param'}
        )
        self.client._handle_response.assert_called_once_with(
            self.session.post.return_value
        )
        self.assertEqual(response, self.client._handle_response.return_value)

    def test_get(self):
        """
        Case: A GET request get executed
        Expected: The correct parameters get given to the request library
        """
        self.client._handle_response = mock.MagicMock()
        response = self.client.get(url='https://example.com/test',
                                   headers={'some': 'header'},
                                   extra='param')

        self.session.get.assert_called_once_with(
            'https://example.com/test',
            headers={'some': 'header'},
            params={'extra': 'param'}
        )

        self.client._handle_response.assert_called_once_with(
            self.session.get.return_value
        )
        self.assertEqual(response, self.client._handle_response.return_value)

    def test_put(self):
        """
        Case: A PUT request get executed
        Expected: The correct parameters get given to the request library
        """
        self.session.return_value.headers = mock.MagicMock()

        self.client._handle_response = mock.MagicMock()
        response = self.client.put(url='https://example.com/test',
                                   data={'some': 'data'},
                                   headers={'some': 'header'},
                                   extra='param')

        self.session.put.assert_called_once_with(
            'https://example.com/test',
            data={'some': 'data'},
            headers={'some': 'header'},
            params={'extra': 'param'}
        )

        self.client._handle_response.assert_called_once_with(
            self.session.put.return_value
        )
        self.assertEqual(response,
                         self.client._handle_response.return_value)

    def test_delete(self):
        """
        Case: A DELETE request get executed
        Expected: The correct parameters get given to the request library
        """
        self.client._handle_response = mock.MagicMock()
        response = self.client.delete(url='https://example.com/test',
                                      headers={'some': 'header'},
                                      extra='param')

        self.session.delete.assert_called_once_with(
            'https://example.com/test',
            headers={'some': 'header'},
            extra='param'
        )
        self.assertEqual(response,
                         self.session.delete.return_value)

    def test_handle_response(self):
        """
        Case: Response get processed
        Expected: Decoded json get returned else raw_response
        """
        response = mock.MagicMock()

        processed_response = self.client._handle_response(response=response)

        response.raise_for_status.assert_called_once_with()
        response.json.assert_called_once_with()

        self.assertEqual(processed_response, response.json.return_value)

        response.json.side_effect = ValueError
        processed_response = self.client._handle_response(response=response)

        self.assertEqual(processed_response, response.content)
