import sys
import os
import logging
import yaml
from logging import SMTPHandler

INTERP = os.path.join(os.environ['HOME'], 'flask_env', 'bin', 'python')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())
from website import app as application

config = yaml.load(file('config.yml').read())
mail_handler = SMTPHandler(config['mail']['smtp'], config['mail']['from'],
                           config['mail']['errors'], config['mail']['errorsubject'])

mail_handler.setLevel(logging.ERROR)
app.logger.addHandler(mail_handler)
