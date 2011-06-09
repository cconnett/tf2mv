__all__ = ['config', 'database', 'app', 'application']

from config import config
import database

from flask import Flask
application = app = Flask(__name__)

import main
import itemFound
