# ##################################################################################### #
# ISIS File Polling Repository : https://github.com/ISISSoftwareServices/ISISFilePolling
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# ##################################################################################### #
"""
End of run monitor. Detects new runs that arrive and
sends them off to the autoreduction service.
"""

import copy
import csv
import logging
from typing import Optional

from filelock import FileLock, Timeout
import requests
from requests.models import Response

from autoreduce_run_detection.settings import LOCAL_CACHE_LOCATION, AUTOREDUCE_API_URL, AUTOREDUCE_TOKEN, TEAMS_URL

# pylint:disable=abstract-class-instantiated

LOGGING = logging.getLogger(__package__)

TEAMS_CARD_DATA = {
    "@context": "https://schema.org/extensions",
    "@type": "MessageCard",
    "themeColor": "0072C6",
    "title": "Alert Raised",
    "text": "",
    "potentialAction": []
}


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
                 file_ext: str = "",
                 teams_url: Optional[str] = None):
        self.instrument_name = instrument_name
        self.last_run_file = last_run_file
        self.summary_file = summary_file
        self.data_dir = data_dir
        self.file_ext = file_ext
        self.teams_url = teams_url

    def read_instrument_last_run(self):
        """
        Read the last run recorded by the instrument from its lastrun.txt

        Returns:
            Last run on the instrument as a string
        """
        with open(self.last_run_file, 'r') as last_run:
            line_parts = last_run.readline().split()
            if len(line_parts) != 3:
                raise InstrumentMonitorError("Unexpected last run file format for '{}'".format(self.last_run_file))
        return line_parts

    def submit_runs(self, start_run, end_run) -> Response:
        """
        Submit a run via the REST API

        Args:
            summary_rb_number: RB number of the experiment as read from the summary file
            run_number: Run number as it appears in lastrun.txt
            file_name: File name e.g. GEM1234.nxs
        """
        # Check to see if the last run exists, if not then raise an exception
        LOGGING.info(
            "Submitting runs in range %i - %i for %s",
            start_run,
            end_run,
            self.instrument_name,
        )
        try:
            response = requests.post(
                AUTOREDUCE_API_URL.format(instrument=self.instrument_name),
                json={
                    "runs": list(range(start_run, end_run + 1)) if abs(end_run - start_run) > 0 else [start_run],
                    "user_id": 0  # AUTOREDUCTTION_SERVICE user id
                },
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Token {AUTOREDUCE_TOKEN}"
                })

            if response.status_code != 200:
                LOGGING.error("Request error when submitting runs in range %i - %i for %s, error: %s", start_run,
                              end_run, self.instrument_name, response.content)
                raise InstrumentMonitorError(f"Request status code is not 200, error: {response.content}")
            return response
        except requests.exceptions.RequestException as err:
            LOGGING.error("Failed to submit runs %i - %i for instrument %s", start_run, end_run, self.instrument_name)
            if self.teams_url:
                data = copy.deepcopy(TEAMS_CARD_DATA)
                data["text"] = f"Failed to submit runs {start_run} - {end_run} for instrument {self.instrument_name}"
                try:
                    requests.post(self.teams_url, json=data)
                except requests.exceptions.RequestException:
                    LOGGING.error("Failed to send message using this TEAMS url: %s", self.teams_url)
            else:
                LOGGING.info("No TEAMS_URL set, not sending message to Teams")
            raise InstrumentMonitorError() from err

    def submit_run_difference(self, local_last_run):
        """
        Submit the difference between the last run on the archive for this
        instrument
        Args:
            local_last_run: Local last run to check against
        """
        # Get archive lastrun.txt
        last_run_data = self.read_instrument_last_run()
        instrument_last_run = last_run_data[1]

        local_run_int = int(local_last_run)
        instrument_run_int = int(instrument_last_run)

        if instrument_run_int > local_run_int:
            LOGGING.info(self.submit_runs(local_run_int + 1, instrument_run_int + 1))
        return str(instrument_run_int)


def update_last_runs(csv_name):
    """
    Read the last runs CSV file and bring it up to date with the
    instrument lastrun.txt

    Args:
        csv_name: File name of the local last runs CSV file
    """
    # Loop over instruments
    output = []
    with open(csv_name, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            LOGGING.info("Processing instrument %s with last run %i", row[0], int(row[1]))
            inst_mon = InstrumentMonitor(instrument_name=row[0],
                                         last_run_file=row[2],
                                         summary_file=row[3],
                                         data_dir=row[4],
                                         file_ext=row[5],
                                         teams_url=TEAMS_URL)

            try:
                last_run = inst_mon.submit_run_difference(row[1])
                row[1] = last_run
            except InstrumentMonitorError as ex:
                LOGGING.error(ex)
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
        LOGGING.error("Error acquiring lock on last runs CSV." " There may be another instance running.")


if __name__ == '__main__':
    main()  # pragma: no cover
