# ##################################################################################### #
# ISIS File Polling Repository : https://github.com/ISISSoftwareServices/ISISFilePolling
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# ##################################################################################### #
"""
End of run monitor. Detects new runs that arrive and
sends them off to the autoreduction service.
"""

import csv
import logging

from filelock import FileLock, Timeout
import requests
from requests.models import Response

from autoreduce_run_detection.settings import LOCAL_CACHE_LOCATION, AUTOREDUCE_API_URL, AUTOREDUCE_TOKEN

INGEST_LOG = logging.getLogger('ingest')


class InstrumentMonitorError(Exception):
    """
    Any fatal exception that occurs during execution of the
    instrument monitor
    """


class InstrumentMonitor:
    """
    Checks the ISIS archive for new runs on an instrument and submits them to ActiveMQ
    """
    def __init__(self,
                 instrument_name: str,
                 last_run_file: str = "",
                 summary_file: str = "",
                 data_dir: str = "",
                 file_ext: str = ""):
        self.instrument_name = instrument_name
        self.last_run_file = last_run_file
        self.summary_file = summary_file
        self.data_dir = data_dir
        self.file_ext = file_ext

    def read_instrument_last_run(self):
        """
        Read the last run recorded by the instrument from its lastrun.txt
        :return: Last run on the instrument as a string
        """
        with open(self.last_run_file, 'r') as last_run:
            line_parts = last_run.readline().split()
            if len(line_parts) != 3:
                raise InstrumentMonitorError("Unexpected last run file format for '{}'".format(self.last_run_file))
        return line_parts

    def submit_runs(self, start_run, end_run) -> Response:
        """
        Submit a run to ActiveMQ
        :param summary_rb_number: RB number of the experiment as read from the summary file
        :param run_number: Run number as it appears in lastrun.txt
        :param file_name: File name e.g. GEM1234.nxs
        """
        # Check to see if the last run exists, if not then raise an exception
        INGEST_LOG.info(
            "Submitting runs in range %i - %i for %s",
            start_run,
            end_run,
            self.instrument_name,
        )
        try:
            response = requests.post(AUTOREDUCE_API_URL.format(instrument=self.instrument_name,
                                                               start_run=start_run,
                                                               end_run=end_run),
                                     headers={
                                         "Content-Type": "application/json",
                                         "Authorization": f"Token {AUTOREDUCE_TOKEN}"
                                     })
            return response
        except requests.exceptions.RequestException as err:
            raise InstrumentMonitorError() from err

    def submit_run_difference(self, local_last_run):
        """
        Submit the difference between the last run on the archive for this
        instrument
        :param local_last_run: Local last run to check against
        """
        # Get archive lastrun.txt
        last_run_data = self.read_instrument_last_run()
        instrument_last_run = last_run_data[1]

        local_run_int = int(local_last_run)
        instrument_run_int = int(instrument_last_run)

        if instrument_run_int > local_run_int:
            INGEST_LOG.info(self.submit_runs(local_run_int + 1, instrument_run_int + 1))
        return str(instrument_run_int)


def update_last_runs(csv_name):
    """
    Read the last runs CSV file and bring it up to date with the
    instrument lastrun.txt
    :param csv_name: File name of the local last runs CSV file
    """
    # Loop over instruments
    output = []
    with open(csv_name, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            inst_mon = InstrumentMonitor(instrument_name=row[0],
                                         last_run_file=row[2],
                                         summary_file=row[3],
                                         data_dir=row[4],
                                         file_ext=row[5])

            try:
                last_run = inst_mon.submit_run_difference(row[1])
                row[1] = last_run
            except InstrumentMonitorError as ex:
                INGEST_LOG.error(ex)
            output.append(row)

    # Write any changes to the CSV
    with open(csv_name, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        for row in output:
            csv_writer.writerow(row)


def main():
    """
    Ingestion Entry point
    """
    # Acquire a lock on the last runs CSV file to prevent access
    # by other instances of this script
    try:
        with FileLock("{}.lock".format(LOCAL_CACHE_LOCATION), timeout=1):
            update_last_runs(LOCAL_CACHE_LOCATION)
    except Timeout:
        INGEST_LOG.error(("Error acquiring lock on last runs CSV." " There may be another instance running."))


if __name__ == '__main__':
    main()  # pragma: no cover
