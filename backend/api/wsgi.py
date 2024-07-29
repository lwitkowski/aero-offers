import sys
import os
# make sure upper folders are reachable (classifier, ...)
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)) + '/..')

import flask_app

application = flask_app.app
