# ##################################################################################### #
# ISIS File Polling Repository : https://github.com/ISISSoftwareServices/ISISFilePolling
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# ##################################################################################### #
# pylint: skip-file
"""
Settings for End of run monitor
"""
import os

# Data Cache
INST_FOLDER = os.path.join('data-archive', 'NDX%s', 'Instrument')
DATA_LOC = os.path.join('data', 'cycle_%s')
SUMMARY_LOC = os.path.join('logs', 'journal', 'summary.txt')
CYCLE_FOLDER = "cycle_18_4"
LAST_RUN_LOC = os.path.join('logs', 'lastrun.txt')

# Instruments
INSTRUMENTS = [{'name': 'WISH', 'use_nexus': True},
               {'name': 'GEM', 'use_nexus': True},
               {'name': 'OSIRIS', 'use_nexus': True},
               {'name': 'POLARIS', 'use_nexus': True},
               {'name': 'MUSR', 'use_nexus': True},
               {'name': 'POLREF', 'use_nexus': True}]

# Message Broker settings
HOST = ''
USER = ''
PASSWORD = ''
PORT = ''
