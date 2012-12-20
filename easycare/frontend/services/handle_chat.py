#-*-coding: utf-8 -*-
import string
import sys, os
import datetime
import re
from django.template.loader import render_to_string

PROJECT_PATH = "/home/easycare/workspace/easycare/easycare"

from django.core.management import setup_environ
sys.path.append(os.path.join(PROJECT_PATH, "easycare"))
import settings
setup_environ(settings)

from frontend.models import *
from frontend.handlers import ChatHandler
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
	print received_number, received_body, contact_number, patient, period
	if contact_number in storeNumber and period:
		record, messages = handler.save_and_get_messages(period = period)
		html_messages = render_to_string('email/confirm_record.html', { 'record': record })
		sent = send_messages_to_patient(patient.confirm_by, patient.contact_number, patient.email, messages, html_messages)
		if not sent:
			record.status = "รอการตอบกลับ และยังไม่ได้รับ SMS ยืนยัน"
			record.save()
	else:
		send_messages_to_patient('sms', contact_number, '', 'ท่านทำรายการไม่ถูกต้อง', '')

