import sys
import os
import logging
import yaml
from logging.handlers import SMTPHandler

INTERP = os.path.join(os.environ['HOME'], 'flask_env', 'bin', 'python')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())
from website import app as application, config

mail_handler = SMTPHandler(config['mail']['smtp'], config['mail']['from'],
                           config['mail']['errors'], config['mail']['errorsubject'])

mail_handler.setLevel(logging.ERROR)
application.logger.addHandler(mail_handler)
