import os
import yaml

config = yaml.load(file(os.path.join(os.path.dirname(__file__), 'config.yml')).read())
