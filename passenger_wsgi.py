import sys
import os

INTERP = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'python')

if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())

from website import application, config

import logging
from handlers import SMTPHandler
# This handlers comes from ./handlers.py, which is a checkout of
# Python 2.7's handlers.  This is needed for authenticated SMTP on
# Python 2.5.

credentials = None
if 'credentials' in config['mail']:
    credentials = (config['mail']['credentials']['username'],
                   config['mail']['credentials']['password'])
mail_handler = SMTPHandler(config['mail']['smtp'], config['mail']['from'],
                           config['mail']['errors'], config['mail']['errorsubject'],
                           credentials)
mail_handler.setLevel(logging.ERROR)
application.logger.addHandler(mail_handler)
