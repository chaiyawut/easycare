import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'easycare.settings'

import django.core.handlers.wsgi
_application = django.core.handlers.wsgi.WSGIHandler()
def application(environ, start_response):
  os.environ['DJANGO_ENV'] = environ['DJANGO_ENV']
  return _application(environ, start_response)
