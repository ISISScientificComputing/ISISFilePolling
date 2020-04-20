import os
LOG_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

LOCAL_CACHE_LOCATION = os.path.join(LOG_DIR, 'last_run.csv')
INGEST_LOG_LOCATION = os.path.join(LOG_DIR, 'ingest.log')
MESSAGE_BROKER_LOG_LOCATION = os.path.join(LOG_DIR, 'message_broker.log')
