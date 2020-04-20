# ##################################################################################### #
# ISIS File Polling Repository : https://github.com/ISISSoftwareServices/ISISFilePolling
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# ##################################################################################### #
# pylint:skip-file
"""
Setup for the project
"""

from setuptools import setup

setup_requires = ['filelock',
                  'nexusformat',
                  'stomp.py',]

setup(name='ISISFilePolling',
      version='0.1',
      description='A service to discover and ingest new files produced by the ISIS neutron and muon facility',
      author='ISIS Scientific Software Group',
      url='https://github.com/ISISSoftwareServices/ISISFilePolling/',
      install_requires=setup_requires,)
