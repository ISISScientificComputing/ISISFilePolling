# ##################################################################################### #
# ISIS File Polling Repository : https://github.com/ISISSoftwareServices/ISISFilePolling
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# ##################################################################################### #
"""
Test that the settings file is moved to it's correct location of travis.
"""
import unittest
import os

from mock import patch


class TestSetupTestEnvironment(unittest.TestCase):
    """ Exercise the setup test environment script """

    @patch('shutil.copyfile')
    def test_settings_file_migration(self, mock_copyfile):
        """
        Test: That the test settings file path is discovered and the file is copied to
              an equivalent settings.py file
        When: The setup_test_environment script is run (in this case imported)
        """
        # pylint:disable=import-outside-toplevel
        # pragma: no cover
        from src.build_config.setup_test_environment import TEST_SETTINGS_FILE, DESTINATION
        self.assertTrue(TEST_SETTINGS_FILE.endswith('test_settings.py'))
        self.assertTrue(DESTINATION.endswith('settings.py'))
        self.assertEqual(os.path.dirname(TEST_SETTINGS_FILE), os.path.dirname(DESTINATION))
        mock_copyfile.assert_called_once_with(TEST_SETTINGS_FILE, DESTINATION)
