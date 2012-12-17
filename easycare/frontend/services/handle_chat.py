#-*-coding: utf-8 -*-
import string
import sys, os
import datetime
import re

PROJECT_PATH = "/home/easycare/workspace/easycare/easycare"

from django.core.management import setup_environ
sys.path.append(os.path.join(PROJECT_PATH, "easycare"))
import settings
setup_environ(settings)

from frontend.models import *
from frontend.handlers import ChatHandler
from freeswitch import *
from frontend.services.send_sms import sendSMSFromWeb
from frontend.utils.words import *

def chat(message, args):
	received_number = message.getHeader("from")
	received_body = message.getBody()
	handler = ChatHandler(received_number, received_body)
	contact_number = handler.get_contact_number()
	period = handler.get_period()
	storeNumber = Patient.objects.all().values_list('contact_number', flat=True)
	if contact_number in storeNumber and period:
		record, messages = handler.save_and_get_messages(period = period)
	elif not period:
		messages =  ["ท่านระบุช่วงเวลาไม่ถูกต้อง"]
	elif not contact_number in storeNumber:
		messages =  ["เบอร์ของท่านไม่ได้ลงทะเบียนในระบบ"]
	sent = sendSMSFromWeb(contact_number, messages)
	if not sent:
		record.status = "รอการตอบกลับ และยังไม่ได้รับ SMS ยืนยัน"
		record.save()
