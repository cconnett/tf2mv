import sys
import os

INTERP = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'python')

if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())

from website import application, config

import logging
from logging.handlers import SMTPHandler

mail_handler = SMTPHandler(config['mail']['smtp'], config['mail']['from'],
                           config['mail']['errors'], config['mail']['errorsubject'])
mail_handler.setLevel(logging.ERROR)
application.logger.addHandler(mail_handler)
