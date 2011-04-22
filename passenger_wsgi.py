import sys
import os
import logging
from logging import SMTPHandler

INTERP = os.path.join(os.environ['HOME'], 'flask_env', 'bin', 'python')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())
from website import app as application

mail_handler = SMTPHandler('mail.tf2mv.com', 'no-reply@tf2mv.com',
                           'errors@tf2mv.com', 'tf2mv Error Logged')

mail_handler.setLevel(logging.ERROR)
app.logger.addHandler(mail_handler)
