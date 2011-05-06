import os
import yaml

filename = os.path.join(os.path.dirname(__file__), 'config.yml')

if not os.path.exists(filename):
    raise EnvironmentError("Missing config.yml file.  Please check your configuration file.")

config = yaml.load(file(filename).read())
