import os
import sys

path = '/home/easycare/workspace/easycare'
if path not in sys.path:
    sys.path.insert(0, path)

esl_lib = '/usr/src/freeswitch/libs/esl/python'
if esl_lib not in sys.path:
    sys.path.insert(0, esl_lib)

os.environ['DJANGO_SETTINGS_MODULE'] = 'easycare.settings'

import django.core.handlers.wsgi
_application = django.core.handlers.wsgi.WSGIHandler()
def application(environ, start_response):
  os.environ['DJANGO_ENV'] = environ['DJANGO_ENV']
  return _application(environ, start_response)
