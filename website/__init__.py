__all__ = ['config', 'app', 'application']

from config import config

from flask import Flask
application = app = Flask(__name__)

import main
import itemFound
