import importlib
import os
import logging
from waitress import serve
from dotenv import load_dotenv
from paste.translogger import TransLogger

logger = logging.getLogger('waitress')
logger.setLevel(logging.DEBUG)

load_dotenv()

search = importlib.import_module("intelligent-search")
target_port = os.getenv("PORT")

print("Running app on 0.0.0.0 and " + target_port + " port!")

serve(TransLogger(search.app, setup_console_handler=False), host='0.0.0.0', port=target_port)
