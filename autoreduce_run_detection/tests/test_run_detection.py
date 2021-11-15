# ##################################################################################### #
# ISIS File Polling Repository : https://github.com/ISISSoftwareServices/ISISFilePolling
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# ##################################################################################### #
"""
Unit tests for run_detection
"""
import logging
import unittest
import os
import csv
from requests.exceptions import RequestException, ConnectionError
from parameterized import parameterized
from filelock import FileLock
from mock import Mock, patch, call

from autoreduce_run_detection.run_detection import InstrumentMonitor, InstrumentMonitorError, update_last_runs, main
from autoreduce_run_detection.settings import AUTOREDUCE_API_URL, LOCAL_CACHE_LOCATION

# Test data
SUMMARY_FILE = ("WIS44731Smith,Smith,"
                "SmithCeAuSb2 MRSX ROT=15.05 s28-MAR-2019 09:14:23    34.3 1820461\n"
                "WIS44732Smith,Smith,"
                "SmithCeAuSb2 MRSX ROT=15.05 s28-MAR-2019 10:23:47    40.0 1820461\n"
                "WIS44733Smith,Smith,"
                "SmithCeAuSb2 MRSX ROT=15.05 s28-MAR-2019 11:34:25     9.0 1820461\n")
LAST_RUN_FILE = "WISH 00044733 0 \n"
INVALID_LAST_RUN_FILE = "INVALID LAST RUN FILE"
RUN_DICT = {
    'instrument': 'WISH',
    'run_number': '00044733',
    'data': '/my/data/dir/cycle_18_4/WISH00044733.nxs',
    'rb_number': '1820461',
    'facility': 'ISIS',
    'started_by': 0
}
RUN_DICT_SUMMARY = {
    'instrument': 'WISH',
    'run_number': '00044733',
    'data': '/my/data/dir/cycle_18_4/WISH00044733.nxs',
    'rb_number': '1820333',
    'facility': 'ISIS'
}
CSV_FILE = "WISH,44733,lastrun_wish.txt,summary_wish.txt,data_dir,.nxs"
LASTRUN_WISH_TXT = "WISH 44734 0"


# pylint:disable=too-few-public-methods,missing-function-docstring
class DataHolder:
    """
    Small helper class to represent expected nexus data format
    """
    def __init__(self, data):
        self.data = data

    def get(self, _):
        mock_value = Mock()
        mock_value.value = self.data
        return mock_value


# nexusformat mock objects
NXLOAD_MOCK = Mock()
NXLOAD_MOCK.items = Mock(return_value=[('raw_data_1', DataHolder([b'1910232']))])

NXLOAD_MOCK_EMPTY = Mock()
NXLOAD_MOCK_EMPTY.items = Mock(return_value=[('raw_data_1', DataHolder(['']))])


class TestRunDetection(unittest.TestCase):
    def tearDown(self):
        if os.path.isfile('test_lastrun.txt'):
            os.remove('test_lastrun.txt')
        if os.path.isfile('test_summary.txt'):
            os.remove('test_summary.txt')
        if os.path.isfile('test_last_runs.csv'):
            os.remove('test_last_runs.csv')
        if os.path.isfile('lastrun_wish.txt'):
            os.remove('lastrun_wish.txt')

    def test_read_instrument_last_run(self):
        with open('test_lastrun.txt', 'w') as last_run:
            last_run.write(LAST_RUN_FILE)

        inst_mon = InstrumentMonitor('WISH')
        inst_mon.last_run_file = 'test_lastrun.txt'
        last_run_data = inst_mon.read_instrument_last_run()

        self.assertEqual('WISH', last_run_data[0])
        self.assertEqual('00044733', last_run_data[1])
        self.assertEqual('0', last_run_data[2])

    # pylint:disable=invalid-name
    def test_read_instrument_last_run_invalid_length(self):
        with open('test_lastrun.txt', 'w') as last_run:
            last_run.write(INVALID_LAST_RUN_FILE)

        inst_mon = InstrumentMonitor('WISH')
        inst_mon.last_run_file = 'test_lastrun.txt'
        with self.assertRaises(InstrumentMonitorError):
            inst_mon.read_instrument_last_run()

    def test_submit_run_difference(self):
        # Setup test
        inst_mon = InstrumentMonitor('WISH')
        inst_mon.submit_runs = Mock(return_value=None)
        inst_mon.file_ext = '.nxs'
        inst_mon.read_instrument_last_run = Mock(return_value=['WISH', '00044733', '0'])

        # Perform test
        run_number = inst_mon.submit_run_difference(44731)
        self.assertEqual(run_number, '44733')
        inst_mon.submit_runs.assert_has_calls([call(44732, 44734)])

    @patch('autoreduce_run_detection.run_detection.requests.post', return_value=[44734, 44735])
    def test_update_last_runs(self, requests_post_mock: Mock):
        # write out the local lastruns.csv that is used to track each instrument
        with open('test_last_runs.csv', 'w') as last_runs:
            last_runs.write(CSV_FILE)

        # write out the lastruns.txt file that would usually be on the archive
        with open('lastrun_wish.txt', 'w') as lastrun_wish:
            lastrun_wish.write(LASTRUN_WISH_TXT)

        # Perform test
        update_last_runs('test_last_runs.csv')
        requests_post_mock.assert_called_once()
        assert requests_post_mock.call_args[0][0] == AUTOREDUCE_API_URL.format(instrument="WISH")
        assert "json" in requests_post_mock.call_args[1]
        assert "headers" in requests_post_mock.call_args[1]

        assert requests_post_mock.call_args[1]["json"]["runs"] == [44734, 44735]
        assert requests_post_mock.call_args[1]["json"]["user_id"] == 0

        # Read the CSV and ensure it has been updated
        with open('test_last_runs.csv') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                if row:  # Avoid the empty rows
                    self.assertEqual('44734', row[1])

    @parameterized.expand([
        [ConnectionError],
        [RequestException],
    ])
    @patch('autoreduce_run_detection.run_detection.requests.post', return_value=[44734, 44735])
    @patch('autoreduce_run_detection.run_detection.LOGGING')
    def test_update_last_runs_with_error(self, exception_class, logger_mock: Mock, requests_post_mock: Mock):
        """
        Test trying to update last runs but the request to the autoreduce API fails.
        """
        # Setup test
        requests_post_mock.side_effect = exception_class
        with open('test_last_runs.csv', 'w') as last_runs:
            last_runs.write(CSV_FILE)

        # write out the lastruns.txt file that would usually be on the archive
        with open('lastrun_wish.txt', 'w') as lastrun_wish:
            lastrun_wish.write(LASTRUN_WISH_TXT)

        # Perform test
        update_last_runs('test_last_runs.csv')
        requests_post_mock.asssert_called_once()

        # Read the CSV and ensure it has been updated
        with open('test_last_runs.csv') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                if row:  # Avoid the empty rows
                    self.assertEqual('44733', row[1])

        assert logger_mock.info.call_count == 2
        assert logger_mock.error.call_count == 2

    @parameterized.expand([
        [ConnectionError],
        [RequestException],
    ])
    @patch('autoreduce_run_detection.run_detection.requests.post', return_value=[44734, 44735])
    @patch('autoreduce_run_detection.run_detection.LOGGING')
    @patch('autoreduce_run_detection.run_detection.TEAMS_URL', return_value="http://fake_url")
    def test_update_last_runs_with_error_and_teams_url_also_fails(self, exception_class, _: Mock, logger_mock: Mock,
                                                                  requests_post_mock: Mock):
        """
        Test trying to update last runs but both the request to the
        autoreduce API and the request to the teams API fail.
        """
        # Setup test
        requests_post_mock.side_effect = exception_class
        with open('test_last_runs.csv', 'w') as last_runs:
            last_runs.write(CSV_FILE)

        # write out the lastruns.txt file that would usually be on the archive
        with open('lastrun_wish.txt', 'w') as lastrun_wish:
            lastrun_wish.write(LASTRUN_WISH_TXT)

        # Perform test
        update_last_runs('test_last_runs.csv')
        requests_post_mock.asssert_called_once()

        # Read the CSV and ensure it has been updated
        with open('test_last_runs.csv') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                if row:  # Avoid the empty rows
                    self.assertEqual('44733', row[1])

        logger_mock.info.assert_called_once()
        assert logger_mock.error.call_count == 3

    @patch(
        'autoreduce_run_detection.run_detection.requests.post',
        return_value=[44734, 44735],
        side_effect=[RequestException, None]  # this means the second call will NOT raise an exception
    )
    @patch('autoreduce_run_detection.run_detection.LOGGING')
    @patch('autoreduce_run_detection.run_detection.TEAMS_URL', return_value="http://fake_url")
    def test_update_last_runs_with_error_and_teams_url(self, teams_url: Mock, logger_mock: Mock,
                                                       requests_post_mock: Mock):
        """
        Test trying to update last runs but the request to the autoreduce API fails.
        The request to the teams API does not raise an exception in this test, i.e. the success path.
        """
        # Setup test
        with open('test_last_runs.csv', 'w') as last_runs:
            last_runs.write(CSV_FILE)

        # write out the lastruns.txt file that would usually be on the archive
        with open('lastrun_wish.txt', 'w') as lastrun_wish:
            lastrun_wish.write(LASTRUN_WISH_TXT)

        # Perform test
        update_last_runs('test_last_runs.csv')
        requests_post_mock.asssert_called_once()

        # Read the CSV and ensure it has been updated
        with open('test_last_runs.csv') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                if row:  # Avoid the empty rows
                    self.assertEqual('44733', row[1])

        logger_mock.info.assert_called_once()
        assert logger_mock.error.call_count == 2

        assert requests_post_mock.call_count == 2
        assert teams_url in requests_post_mock.call_args[0]

    @patch('autoreduce_run_detection.run_detection.update_last_runs')
    def test_main(self, update_last_runs_mock):
        main()
        update_last_runs_mock.assert_called_with(LOCAL_CACHE_LOCATION)
        update_last_runs_mock.assert_called_once()

    @patch('autoreduce_run_detection.run_detection.update_last_runs')
    def test_main_lock_timeout(self, _):
        with FileLock('{}.lock'.format(LOCAL_CACHE_LOCATION)):
            main()
