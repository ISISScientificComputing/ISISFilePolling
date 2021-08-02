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
from autoreduce_utils.settings import AUTOREDUCE_HOME_ROOT

LOCAL_CACHE_LOCATION = os.path.join(AUTOREDUCE_HOME_ROOT, 'last_runs.csv')

# Data Cache
CYCLE_FOLDER = "cycle_22_1"

AUTOREDUCE_API_URL = "http://reduce.isis.cclrc.ac.uk/api/runs/{instrument}/{start_run}/{end_run}"
AUTOREDUCE_TOKEN = os.environ.get('AUTOREDUCE_TOKEN')