#-*-coding: utf-8 -*-
from frontend.models import *
from frontend.utils.words import *
from frontend.services.send_messages_to_patient import send_messages_to_patient
from django.template.loader import render_to_string
import re

class ChatHandler:
	def __init__(self, received_number, received_body):
		self.received_number = received_number
		self.received_body = received_body
		self.weight = {}
		self.drug = {}
		self.pressure = {}

	def get_patient(self):
		try:
			contact_number = self.get_contact_number()
			patient = Patient.objects.get(contact_number=contact_number)
		except Exception, e:
			return None
		return patient

	def get_contact_number(self):
		try:
			contect_number = '0' + re.match(r"\+66(\d+)", self.received_number).group(1)
		except Exception, e:
			return None
		return contect_number

	def get_period(self):
		try:
			p_num = re.search(r"p(\d{1})", self.received_body, flags=re.IGNORECASE).group(1)
		except Exception, e:
			return None
		if p_num == '1':
			period = 'morning'
		elif p_num == '2':
			period = 'afternoon'
		elif p_num == '3':
			period = 'evening'
		else:
			return None
		return period

	def get_weight(self):
		try:
			self.weight['weight'] = re.search(r"w(\d+.\d*)", self.received_body, flags=re.IGNORECASE).group(1)
		except Exception, e:
			return None
		if float(self.weight['weight']) > 200 or float(self.weight['weight']) < 0:
			return None
		else:
			return self.weight

	def get_pressure(self):
		try:
			self.pressure['up'] = re.search(r"bp(\d+)/(\d+)", self.received_body, flags=re.IGNORECASE).group(1)
			self.pressure['down'] = re.search(r"bp(\d+)/(\d+)", self.received_body, flags=re.IGNORECASE).group(2)
		except Exception, e:
			return None
		if float(self.pressure['up']) > 200 or float(self.pressure['up']) < 0 or float(self.pressure['down']) > 200 or float(self.pressure['down']) < 0:
			return None
		else:
			return self.pressure

	def get_drug(self):
		try:
			self.drug['name'] = DRUG_NAMES[re.search(r"(\w)\d+mg\d+\.?\d*", self.received_body, flags=re.IGNORECASE).group(1)]
			self.drug['size'] = re.search(r"l(\d+)mg(\d+\.?\d*)", self.received_body, flags=re.IGNORECASE).group(1)
			self.drug['amount'] = re.search(r"l(\d+)mg(\d+\.?\d*)", self.received_body, flags=re.IGNORECASE).group(2)
		except Exception, e:
			return None
		if not self.drug['name'] or float(self.drug['size']) not in [40,500] or float(self.drug['amount']) > 5 or float(self.drug['amount']) < 0:
			return None
		else :
			return self.drug

	def save_and_get_messages(self, period):
		patient = self.get_patient()
		weight = self.get_weight()
		pressure = self.get_pressure()
		drug = self.get_drug()

		if period == '':
			html_messages = 'ท่านทำรายการไม่ถูกต้อง กรุณาระบุช่วงเวลาด้วยสัญลักษณ์ p หรือ P'
			messages = "ท่านทำรายการไม่ถูกต้อง กรุณาระบุช่วงเวลา"
		if not patient.check_for_no_duplicate_period(period):
			submitted_records = Record.objects.filter( datetime__range=(datetime.datetime.combine(now.date(), datetime.time.min).replace(tzinfo=timezone.get_default_timezone()),
                            datetime.datetime.combine(now.date(), datetime.time.max).replace(tzinfo=timezone.get_default_timezone()))).exclude(response__deleted=True)
			html_messages = render_to_string('email/duplicate_records.html', { 'HEADER':'เกิดข้อผิดพลาด! ท่านได้ส่งข้อมูลของช่วงเวลานี้แล้ว','submitted_records': submitted_records })
			messages = "ท่านได้ส่งข้อมูลของช่วงเวลานี้แล้ว "
		elif not weight and not pressure and not drug:
			html_messages = "ผิดพลาด ท่านไม่ได้ใส่ข้อมูลเลย กรุณาใส่ข้อมูล"
			messages =  "ผิดพลาด ท่านไม่ได้ใส่ข้อมูลเลย กรุณาใส่ข้อมูล"
		else:
			record = patient.create_new_record(period, 'sms')
			messages = '#' + str(record.id) + ' ช่วง:' + PERIODS[period] + ' '
			if weight:
				weight_entry = record.create_entry_for_record_from_voip(weight=weight)
				messages = messages + "น้ำหนัก:" + str(weight_entry.weight) + " "
			if drug:
				drug_entry = record.create_entry_for_record_from_voip(drug=drug)
				messages = messages + "ยา:" + str(drug_entry.size)+"มก."+ str(drug_entry.amount) + "เม็ด "
			if pressure:
				pressure_entry = record.create_entry_for_record_from_voip(pressure=pressure)
				messages = messages + "ความดัน:" + str(pressure_entry.up)+"/"+ str(pressure_entry.down) + " "
			#save the whole message to Sign
			record.create_entry_for_record_from_voip(sign=self.received_body)
			html_messages = render_to_string('email/confirm_record.html', { 'record': record })
		
		sent = send_messages_to_patient(patient.confirm_by, patient.contact_number, patient.email, messages, html_messages)
		if not sent:
			record.status = "ระบบส่งข้อความผิดพลาด! ผู้ป่วยยังไม่ได้รับ SMS ยืนยัน"
			record.save()
			
