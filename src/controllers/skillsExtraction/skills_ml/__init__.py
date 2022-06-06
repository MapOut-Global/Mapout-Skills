import logging.config,os
os.makedirs("logs", exist_ok = True)
CONFIG_FILE_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), 'logging.conf'))
logging.config.fileConfig(CONFIG_FILE_PATH, disable_existing_loggers=False)
log = logging.getLogger(__name__)