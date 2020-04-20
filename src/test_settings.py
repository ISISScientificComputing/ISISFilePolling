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

from src.logs import LOG_DIR

# Logging
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_FILE = os.path.join(LOG_DIR, 'isis_file_polling.log')


# Data Cache
INST_FOLDER = os.path.join(get_project_root(), 'data-archive', 'NDX%s', 'Instrument')
DATA_LOC = os.path.join('data', 'cycle_%s')
SUMMARY_LOC = os.path.join('logs', 'journal', 'summary.txt')
CYCLE_FOLDER = "cycle_18_4"

# Last run local cache
LAST_RUN_LOC = os.path.join('logs', 'lastrun.txt')
LAST_RUN_FILE = os.path.join(LOG_DIR, 'last_run.csv')

# Instruments
INSTRUMENTS = [{'name': 'WISH', 'use_nexus': True},
               {'name': 'GEM', 'use_nexus': True},
               {'name': 'OSIRIS', 'use_nexus': True},
               {'name': 'POLARIS', 'use_nexus': True},
               {'name': 'MUSR', 'use_nexus': True},
               {'name': 'POLREF', 'use_nexus': True}]
