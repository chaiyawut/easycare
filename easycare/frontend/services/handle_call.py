#-*-coding: utf-8 -*-
from freeswitch import *
import sys, os

#use relative path need 3 symbolic links in freeswitch to import settings
PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..'))
sys.path.append(os.path.join(PROJECT_PATH, "easycare"))
os.environ['DJANGO_ENV'] = 'production'
import settings
from django.core.management import setup_environ
setup_environ(settings)

from django.conf import settings
settings.configure(CELERY_EAGER_PROPAGATES_EXCEPTIONS = True, CELERY_ALWAYS_EAGER = True, BROKER_BACKEND = 'memory')

from frontend.handlers.call import CallHandler

def input_callback_record_file_pound_stop(session, type, obj):
	return "stop"

def handler(session, args):
	#All mobile incomming calls are now disabled by freeswitch dialplan.
	#All calls are from phone line and no call_id.
	session.answer()
	session.setInputCallback(input_callback_record_file_pound_stop)
	handler = CallHandler(session)
	handler.main_menu()

