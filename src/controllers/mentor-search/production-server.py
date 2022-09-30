import importlib
import os
import logging
from waitress import serve
from dotenv import load_dotenv
from paste.translogger import TransLogger

logger = logging.getLogger('waitress')
logger.setLevel(logging.DEBUG)

load_dotenv()

#
# Python module must be either in python naming convention or imported like in the case below
# https://stackoverflow.com/questions/8350853/how-to-import-module-when-module-name-has-a-dash-or-hyphen-in-it
# https://stackoverflow.com/questions/761519/is-it-ok-to-use-dashes-in-python-files-when-trying-to-import-them
#
# Waitress docs
# https://buildmedia.readthedocs.org/media/pdf/waitress/latest/waitress.pdf
#
# Tip
# Waitress seems to not be the most effective server for Python apps
#
search = importlib.import_module("intelligent-search")
target_port = os.getenv("PORT")

print("Running app on 0.0.0.0 and " + target_port + " port!")
#
# In production Flask app must be served thorough WSGI server
# https://flask.palletsprojects.com/en/2.2.x/deploying/#self-hosted-options
# https://flask.palletsprojects.com/en/2.2.x/deploying/waitress/
# https://stackoverflow.com/questions/51045911/serving-flask-app-with-waitress-on-windows
#
serve(TransLogger(search.app, setup_console_handler=False), host='0.0.0.0', port=target_port)
