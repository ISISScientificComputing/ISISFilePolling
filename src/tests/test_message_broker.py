# ##################################################################################### #
# ISIS File Polling Repository : https://github.com/ISISSoftwareServices/ISISFilePolling
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# ##################################################################################### #
"""
Test functionality for the message broker
"""
import unittest

from mock import patch

from src.message_broker import MessageBrokerClient


# pylint:disable=protected-access,invalid-name,missing-docstring
class TestQueueClient(unittest.TestCase):
    """
    Exercises the queue client
    """

    def test_default_init(self):
        """ Test default values for initialisation """
        client = MessageBrokerClient()
        self.assertIsNotNone(client._host)
        self.assertIsNotNone(client._user)
        self.assertIsNotNone(client._port)
        self.assertIsNotNone(client._pass)
        self.assertIsNone(client._connection)

    def test_valid_connection(self):
        """
        Test connection with valid credentials
        This by proxy will also test the get_connection function
        """
        client = MessageBrokerClient()
        client.connect()
        self.assertTrue(client._test_connection())

    @patch('stomp.connect.StompConnection11.is_connected', return_value=False)
    def test_invalid_connection_raises_on_test(self, _):
        client = MessageBrokerClient()
        client.connect()
        self.assertRaises(RuntimeError, client._test_connection)

    def test_stop_connection(self):
        """ Test connection can be stopped gracefully """
        client = MessageBrokerClient()
        client.connect()
        self.assertTrue(client._connection.is_connected())
        client.disconnect()
        self.assertIsNone(client._connection)

    def test_serialise_message(self):
        """ Test data is correctly serialised """
        client = MessageBrokerClient()
        data = client.serialise_data('123', 'WISH', 'file/path', '001', 0)
        self.assertEqual(data['rb_number'], '123')
        self.assertEqual(data['instrument'], 'WISH')
        self.assertEqual(data['data'], 'file/path')
        self.assertEqual(data['run_number'], '001')
        self.assertEqual(data['facility'], 'ISIS')
        self.assertEqual(data['started_by'], 0)

    # pylint:disable=no-self-use
    @patch('stomp.connect.StompConnection11.send')
    def test_send_data(self, mock_send):
        """ Test data can be sent without error """
        client = MessageBrokerClient()
        client.send('dataready', 'test-message')
        mock_send.assert_called_once()
