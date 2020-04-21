# ##################################################################################### #
# ISIS File Polling Repository : https://github.com/ISISSoftwareServices/ISISFilePolling
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# ##################################################################################### #
"""
Client class for accessing queuing service
"""
import logging
import time

import stomp
from stomp.exception import ConnectFailedException

from src.logs import LOG_FORMAT, MESSAGE_BROKER_LOG_LOCATION
from src.settings import HOST, PASSWORD, USER, PORT

logging.basicConfig(filename=MESSAGE_BROKER_LOG_LOCATION, level=logging.INFO,
                    format=LOG_FORMAT)


class MessageBrokerClient:
    """
    Class for client to access messaging service via python
    """

    def __init__(self, host=None, user=None, password=None, port=None):
        self._host = host if host else HOST
        self._user = user if user else USER
        self._pass = password if password else PASSWORD
        self._port = port if port else PORT

        self._connection = None

    def connect(self):
        """
        Create the connection if the connection has not been created
        :return: connection object
        """
        if self._connection is None or not self._connection.is_connected():
            self.disconnect()
            return self._create_connection()
        return self._connection

    def _test_connection(self):
        if not self._connection.is_connected():
            raise RuntimeError("Unable to connect to message broker")
        return True

    def disconnect(self):
        """
        disconnect from queue service
        """
        logging.info("Disconnecting from activemq")
        if self._connection is not None and self._connection.is_connected():
            self._connection.disconnect()
            self._connection.stop()
        self._connection = None

    def _create_connection(self):
        """
        Get the connection to the queuing service
        :return: The connection to the queue
        """
        if self._connection is None or not self._connection.is_connected():
            try:
                host_port = [(self._host, int(self._port))]
                connection = stomp.Connection(host_and_ports=host_port,
                                              use_ssl=False)
                logging.info("Starting connection to %s", host_port)
                connection.start()
                connection.connect(username=self._user,
                                   passcode=self._pass,
                                   wait=False,
                                   header={'activemq.prefetchSize': '1'})
            except ConnectFailedException:
                raise RuntimeError("Unable to connect to message broker")
            # Sleep required to avoid using the service too quickly after establishing connection
            time.sleep(0.5)
            self._connection = connection
        return self._connection

    def subscribe_queues(self, queue_list, consumer_name, listener, ack='auto'):
        """
        Subscribe a listener to the provided queues
        """
        self._connection.set_listener(consumer_name, listener)
        for queue in queue_list:
            self._connection.subscribe(destination=queue,
                                       id='1',
                                       ack=ack,
                                       header={'activemq.prefetchSize': '1'})
            logging.info("[%s] Subscribing to %s", consumer_name, queue)
        logging.info("Successfully subscribed to all of the queues")

    @staticmethod
    def serialise_data(rb_number, instrument, location, run_number, started_by):
        """
        Packs the specified data into a dictionary ready to send to a processor queue
        """
        return {'rb_number': rb_number,
                'instrument': instrument,
                'data': location,
                'run_number': run_number,
                'started_by': started_by,
                'facility': 'ISIS'}

    # pylint:disable=too-many-arguments
    def send(self, destination, message, persistent='true', priority='4', delay=None):
        """
        Send a message via the open connection to a queue
        :param destination: Queue to send to
        :param message: contents of the message
        :param persistent: should to message be persistent
        :param priority: priority rating of the message
        :param delay: time to wait before send
        """
        self.connect()
        self._connection.send(destination, message,
                              persistent=persistent,
                              priority=priority,
                              delay=delay)