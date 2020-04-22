# ISISFilePolling
[![Build Status](https://travis-ci.com/ISISSoftwareServices/ISISFilePolling.svg?branch=master)](https://travis-ci.com/ISISSoftwareServices/ISISFilePolling)
[![Coverage Status](https://coveralls.io/repos/github/ISISSoftwareServices/ISISFilePolling/badge.svg?branch=master)](https://coveralls.io/github/ISISSoftwareServices/ISISFilePolling?branch=master)


### Description
A service to poll the ISIS Data Cache, discover new files and push them to a broker for ingestion into other associated projects.

### Installation
Requires: Python3.6+, ActiveMQ

1. `git clone https://github.com/ISISSoftwareServices/ISISFilePolling.git`
     1. Optionally setup a python virtualenv to manage package requirements 
2. `pip3 install -e ISISFilePolling
3. `pip3 install -r ISISFilePolling/requirements.txt

### Configuration

1. Copy the `test_settings.py` file to the same directory but rename it to `settings.py`. You can use the script to do this automatically:
`python3 ISISFilePolling/src/build_config/setup_test_environment.py`
2. Update the `settings.py` file to point to desired file systems / services

### Running
1. Setup a cron job to run `ISISFilePolling/src/ingest.py`
