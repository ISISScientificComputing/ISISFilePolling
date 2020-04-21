# ##################################################################################### #
# ISIS File Polling Repository : https://github.com/ISISSoftwareServices/ISISFilePolling
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# ##################################################################################### #
"""
Move the test_settings to the actual settings file for use in tests
"""
import os

from src import test_settings
from shutil import copyfile

TEST_SETTINGS_FILE = os.path.abspath(test_settings.__file__)
DESTINATION = os.path.join(os.path.dirname(TEST_SETTINGS_FILE), 'settings.py')


copyfile(TEST_SETTINGS_FILE, DESTINATION)
