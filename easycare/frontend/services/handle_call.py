#-*-coding: utf-8 -*-
from freeswitch import *
import datetime, sys, os
import re
from django.core.management import setup_environ
from ESL import *
from decimal import Decimal

PROJECT_PATH = "/home/easycare/workspace/easycare/easycare"

sys.path.append(os.path.join(PROJECT_PATH, "easycare"))
os.environ['DJANGO_ENV'] = 'production'
import settings
setup_environ(settings)
from frontend.models import *
from frontend.handlers import CallHandler
from frontend.utils.words import *


def input_callback_record_file_pound_stop(session, type, obj):
	return "stop"

def handler(session, args):
	#All mobile incomming calls are now disabled by freeswitch dialplan.
	#All calls are from phone line and no call_id.
	session.answer()
	session.setInputCallback(input_callback_record_file_pound_stop)
	handler = CallHandler(session)
	handler.main_menu()
	# storeNumber = Patient.objects.all().values_list('contact_number', flat=True)
	# if session.getVariable("caller_id_number") in storeNumber:
	# 	session.answer()
	# 	session.setInputCallback(input_callback_record_file_pound_stop)
	# 	handler = CallHandler(session)
	# 	handler.main_menu()
