import logging.config
import os

logging.config.fileConfig(os.path.dirname(os.path.abspath(__file__)) + os.sep + 'logging.conf')
