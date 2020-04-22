# ##################################################################################### #
# ISIS File Polling Repository : https://github.com/ISISSoftwareServices/ISISFilePolling
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# ##################################################################################### #
"""
Small script used by CI to copy the test_settings.py file to destination settings.py
This will ensure that when running CI the system uses the values defined in the test settings
"""
import os
from shutil import copyfile

from src import test_settings

TEST_SETTINGS_FILE = os.path.abspath(test_settings.__file__)
DESTINATION = os.path.join(os.path.dirname(TEST_SETTINGS_FILE), 'settings.py')

copyfile(TEST_SETTINGS_FILE, DESTINATION)
