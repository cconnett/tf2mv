__all__ = ['config', 'app', 'main', 'itemFound']

import yaml
from flask import Flask

config = yaml.load(file('config.yml').read())
app = Flask(__name__)
