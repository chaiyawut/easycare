#-*-coding: utf-8 -*-
import string
import sys, os
import datetime
import re
from django.template.loader import render_to_string

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..'))

from django.core.management import setup_environ
sys.path.append(os.path.join(PROJECT_PATH, "easycare"))
os.environ['DJANGO_ENV'] = 'production'
import settings
setup_environ(settings)

from frontend.models import *
from frontend.handlers.chat import ChatHandler
from freeswitch import *
from frontend.services.send_messages_to_patient import send_messages_to_patient
from frontend.utils.words import *

def chat(message, args):
	received_number = message.getHeader("from")
	received_body = message.getBody()
	handler = ChatHandler(received_number, received_body)
	contact_number = handler.get_contact_number()
	patient = handler.get_patient()
	period = handler.get_period()
	storeNumber = Patient.objects.all().values_list('contact_number', flat=True)
	if contact_number in storeNumber and period:
		handler.save_and_get_messages(period = period)
	else:
		send_messages_to_patient(patient.confirm_by, patient.contact_number, patient.email, 'ท่านทำรายการไม่ถูกต้อง', 'ท่านทำรายการไม่ถูกต้อง')

