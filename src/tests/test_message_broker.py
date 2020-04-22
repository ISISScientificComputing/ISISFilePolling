# ##################################################################################### #
# ISIS File Polling Repository : https://github.com/ISISSoftwareServices/ISISFilePolling
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# ##################################################################################### #
"""
Test functionality for the message broker
Note: this does not require an AMQ instance to run, all connection calls are mocked
"""
import unittest

from mock import patch, Mock
from stomp.exception import ConnectFailedException

from src.message_broker import MessageBrokerClient


# pylint:disable=protected-access,invalid-name
class TestMessageBrokerClient(unittest.TestCase):
    """
    Exercises the MessageBrokerClient with a Mocked AMQ connection
    """

    @staticmethod
    def _create_client_with_connection(is_connected):
        """
        Create and return a client with a mocked connection
        :param is_connected: if the connection is connected or not
        :return: The client object and the mock (mock returned for comparison - if required)
        """
        mock_connection = Mock()
        mock_connection.is_connected.return_value = is_connected
        client = MessageBrokerClient()
        client._connection = mock_connection
        return client, mock_connection

    def test_default_init(self):
        """
        Test: The client is correctly initialised with default variables
        When: No input is given to __init__
        """
        client = MessageBrokerClient()
        self.assertIsNotNone(client._host)
        self.assertIsNotNone(client._user)
        self.assertIsNotNone(client._port)
        self.assertIsNotNone(client._pass)
        self.assertIsNone(client._connection)

    def test_non_default_init(self):
        """
        Test: The client is correctly initialised
        When: Non-default input is given to __init__
        """
        client = MessageBrokerClient(host='host',
                                     user='user',
                                     port='port',
                                     password='pass')
        self.assertEqual(client._host, 'host')
        self.assertEqual(client._user, 'user')
        self.assertEqual(client._port, 'port')
        self.assertEqual(client._pass, 'pass')

    # pylint:disable=no-self-use
    @patch('src.message_broker.MessageBrokerClient._create_connection')
    @patch('src.message_broker.MessageBrokerClient.disconnect')
    def test_connect_when_connection_is_none(self, mock_disconnect, mock_create_connection):
        """
        Test: _create_connection() is called within connect()
        When: client._connection is None
        """
        client = MessageBrokerClient()
        client._connection = None
        client.connect()
        mock_disconnect.assert_called_once()
        mock_create_connection.assert_called_once()

    @patch('src.message_broker.MessageBrokerClient._create_connection')
    @patch('src.message_broker.MessageBrokerClient.disconnect')
    def test_connect_when_connection_disconnected(self, mock_disconnect, mock_create_connection):
        """
        Test: _create_connection() is called within connect()
        When: client._connection object has been disconnected
        """
        client, _ = self._create_client_with_connection(False)
        client.connect()
        mock_disconnect.assert_called_once()
        mock_create_connection.assert_called_once()

    def test_connect_with_valid_connection(self):
        """
        Test: The existing connection object is returned from connect()
        When: client._connection is connected
        """
        client, mock_connection = self._create_client_with_connection(True)
        actual = client.connect()
        self.assertEqual(mock_connection, actual)

    def test_test_connection_when_connected(self):
        """
        Test: _test_connection() returns True
        When: client._connection is connected
        """
        client, _ = self._create_client_with_connection(True)
        self.assertTrue(client._test_connection())

    def test_test_connection_when_disconnected(self):
        """
        Test: _test_connection() raises a RuntimeError
        When: client._connection is disconnected
        """
        client, _ = self._create_client_with_connection(False)
        self.assertRaises(RuntimeError, client._test_connection)

    def test_disconnect_when_valid_connection(self):
        """
        Test: client.disconnect() correctly disconnects
        When: client._connection is connected
        """
        client, mock_connection = self._create_client_with_connection(True)
        client.disconnect()
        self.assertIsNone(client._connection)
        mock_connection.disconnect.assert_called_once()

    def test_disconnect_when_invalid_connection(self):
        """
        Test: That client.disconnect() makes client._connection None
        When: client._connection is disconnected
        """
        client, mock_connection = self._create_client_with_connection(False)
        client.disconnect()
        self.assertIsNone(client._connection)
        self.assertFalse(mock_connection.disconnect.called)

    def test_disconnect_when_connection_is_none(self):
        """
        Test: No additional functions are called and no variables are changed
        When: calling client.disconnect while client._connection is None
        """
        client = MessageBrokerClient()
        self.assertIsNone(client._connection)
        client.disconnect()
        self.assertIsNone(client._connection)

    def test_create_connection_with_valid_connection(self):
        """
        Test: client._connection is return if calling _create_connection
        When: client._connection is already connected
        """
        client, mock_connection = self._create_client_with_connection(True)
        actual = client._create_connection()
        self.assertEqual(mock_connection, actual)

    @patch('time.sleep')
    @patch('stomp.Connection')
    def test_create_connection_with_invalid_connection(self, mock_stomp, mock_sleep):
        """
        Test: A connected connection is created and returned by calling client._create_connection
        When: client._connection is None or disconnected
        """
        client, _ = self._create_client_with_connection(False)
        expected_stomp = {
            'host_and_ports': [(client._host, int(client._port))],
            'use_ssl': False
        }
        expected_connect = {
            'username': client._user,
            'passcode': client._pass,
            'wait': False,
            'header': {'activemq.prefetchSize': '1'}
        }
        mock_connection = Mock()
        mock_stomp.return_value = mock_connection
        actual = client._create_connection()

        mock_stomp.assert_called_once_with(**expected_stomp)
        mock_connection.connect.assert_called_once_with(**expected_connect)
        mock_sleep.assert_called_once_with(0.5)
        self.assertEqual(client._connection, mock_connection)
        self.assertEqual(actual, mock_connection)

    @patch('stomp.Connection')
    def test_create_connection_raises(self, mock_stomp):
        """
        Test: A RuntimeError is raised by _create_connection()
        When: stomp.Connection raises a ConnectFailedException
        """
        mock_stomp.side_effect = ConnectFailedException
        client, _ = self._create_client_with_connection(False)
        self.assertRaises(RuntimeError, client._create_connection)

    def test_serialise_message(self):
        """
        Test: A dictionary of expected values is returned
        When: serialize_data is called with valid arguments
        """
        client = MessageBrokerClient()
        data = client.serialise_data('123', 'WISH', 'file/path', '001', 0)
        self.assertEqual(data['rb_number'], '123')
        self.assertEqual(data['instrument'], 'WISH')
        self.assertEqual(data['data'], 'file/path')
        self.assertEqual(data['run_number'], '001')
        self.assertEqual(data['facility'], 'ISIS')
        self.assertEqual(data['started_by'], 0)

    def test_send_data(self):
        """
        Test: _connection.send() is called with expected values
        When: client.send() is called
        """
        client, mock_connection = self._create_client_with_connection(True)
        client.send('/dataready', 'test-message')
        expected = {
            'destination': '/dataready',
            'body': 'test-message',
            'persistent': 'true',
            'priority': '4',
            'delay': None,
        }
        mock_connection.send.assert_called_once_with(**expected)
