#-*-coding: utf-8 -*-
import re
from frontend.models import *
import os
from frontend.utils.words import *
from easycare.settings import PROJECT_PATH
from frontend.services.send_messages_to_patient import send_messages_to_patient
from django.template.loader import render_to_string

VOICE_PATH = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'services', 'sounds'))

class CallHandler:
	def __init__(self, session):
		self.session = session
		self.contact_number = ''
		self.period = ''
		self.weight = {}
		self.drug = {}
		self.pressure = {}
		self.voicemail = {}

	def main_menu(self):
		self.session.sleep(200)
		self.session.streamFile(os.path.join(VOICE_PATH, 'welcome.wav'))
		self.session.sleep(1000)
		next_menu = self.login_menu()
		while next_menu:
		   next_menu = next_menu(self.period)
		self.session.streamFile(os.path.join(VOICE_PATH, 'fail.wav'))
		self.session.streamFile(os.path.join(VOICE_PATH, 'thankyou.wav'))

	def login_menu(self):
		self.__init__(self.session)
		self.contact_number = self.get_contact_number()
		storeNumber = Patient.objects.all().values_list('contact_number', flat=True)
		print self.contact_number
		if self.contact_number in storeNumber:
			patient = self.get_patient()
			self.session.sleep(200)
			self.session.streamFile(patient.sound_for_name.path)
			return self.period_menu
		else:
			self.session.streamFile(os.path.join(VOICE_PATH, 'login', 'not_found.wav'))
			self.session.streamFile(os.path.join(VOICE_PATH, 'thankyou.wav'))
			self.session.destroy()

	def period_menu(self):
		self.period = self.get_period()
		if self.period in ['morning', 'afternoon', 'evening']:
			return self.weight_menu

	def weight_menu(self, period):
		response = self.session.playAndGetDigits(
			1, 1, 3, 4000, "",
			os.path.join(VOICE_PATH, 'weight', '1-'+ period +'.wav'),
			os.path.join(VOICE_PATH, 'fail.wav'),
			"[123]")          
		if response == "1":
			weight = self.get_weight()
			if weight:
				self.session.streamFile(os.path.join(VOICE_PATH, 'thankyou.wav'))
				return self.pressure_menu
		elif response == "2":
			return self.pressure_menu
		elif response == "3":
			return self.period_menu

	def pressure_menu(self, period):
		response = self.session.playAndGetDigits(
			1, 1, 3, 4000, "",
			os.path.join(VOICE_PATH, 'pressure', '1-'+ period +'.wav'),
			os.path.join(VOICE_PATH, 'fail.wav'),
			"[123]")
		if response == "1":
			pressure = self.get_pressure()
			if pressure:
				self.session.streamFile(os.path.join(VOICE_PATH, 'thankyou.wav'))
				return self.drug_menu
		elif response == "2":
			return self.drug_menu
		elif response == "3":
			return self.weight_menu

	def drug_menu(self, period):
		response = self.session.playAndGetDigits(
			1, 1, 3, 4000, "",
			os.path.join(VOICE_PATH, 'drug', '1-'+ period +'.wav'),
			os.path.join(VOICE_PATH, 'fail.wav'),
			"[123]")
		if response == "1":
			drug = self.get_drug()
			if drug:
				self.session.streamFile(os.path.join(VOICE_PATH, 'thankyou.wav'))
				return self.voicemail_menu
		elif response == "2":
			return self.voicemail_menu
		elif response == "3":
			return self.pressure_menu

	def voicemail_menu(self, period):
		response = self.session.playAndGetDigits(
			1, 1, 3, 4000, "",
			os.path.join(VOICE_PATH, 'voicemail', '1-'+ period +'.wav'),
			os.path.join(VOICE_PATH, 'fail.wav'),
			"[123]")
		if response == "1":
			voicemail = self.get_voicemail()
			if voicemail:
				self.session.streamFile(os.path.join(VOICE_PATH, 'thankyou.wav'))
				return self.save_menu
		elif response == "2":
			return self.save_menu
		elif response == "3":
			return self.drug_menu


	def save_menu(self, period):
		patient = self.get_patient()
		contact_number = patient.contact_number
		weight = self.weight
		pressure = self.pressure
		drug = self.drug
		voicemail = self.voicemail
		if weight and period in patient.get_today_submitted_periods(entry='weight'):
			messages = ["ท่านได้ส่งข้อมูลน้ำหนักของช่วงเวลานี้แล้ว"]
		elif pressure and period in patient.get_today_submitted_periods(entry='pressure'):
			messages = ["ท่านได้ส่งข้อมูลความดันของช่วงเวลานี้แล้ว"]
		elif drug and period in patient.get_today_submitted_periods(entry='drug'):
			messages =  ["ท่านได้ส่งข้อมูลยาของช่วงเวลานี้แล้ว"]
		elif not voicemail and not weight and not pressure and not drug:
			messages =  ["ผิดพลาด ท่านไม่ได้ใส่ข้อมูลเลย กรุณาใส่ข้อมูล"]
		else:
			record = patient.create_new_record()
			entry_messages = "p:" + PERIODS[period] + " "
			if weight:
				weight_entry = record.create_entry_for_record_from_voip(period, weight=weight)
				entry_messages = entry_messages + "w" + str(weight_entry.weight) + " "
			if pressure:
				pressure_entry = record.create_entry_for_record_from_voip(period, pressure=pressure)
				entry_messages = entry_messages + "bp" + str(pressure_entry.up)+"/"+ str(pressure_entry.down) + " "
			if drug:
				drug_entry = record.create_entry_for_record_from_voip(period, drug=drug)
				entry_messages = entry_messages + "l" + str(drug_entry.size)+"mg"+ str(drug_entry.amount) + " "
			if voicemail:
				record.voicemail = voicemail['path']
				record.save()
			messages =  ["Ref:"+ str(record.id) +" " + entry_messages]

		html_messages = render_to_string('email/confirm_record.html', { 'record': record })
		send_messages_to_patient(patient.confirm_by, patient.contact_number, patient.email, messages, html_messages)

		sent = send_messages_to_patient(patient.confirm_by, '', '', html_messages)
		if not sent:
			record.status = "รอการตอบกลับ และยังไม่ได้รับ SMS ยืนยัน"
			record.save()
		return self.conclude_menu


	def conclude_menu(self, period):
		self.session.streamFile(os.path.join(VOICE_PATH, 'conclude', '1-'+period+'.wav'))
		self.session.streamFile(os.path.join(VOICE_PATH, 'conclude', '2.wav'))
		self.session.sleep(4000)
		return self.period_menu


	def get_contact_number(self):
		contact_number = self.session.playAndGetDigits(
			8, 12, 3, 4000, "#",
			os.path.join(VOICE_PATH, 'login', '1.wav'),
			os.path.join(VOICE_PATH, 'fail.wav'),
			"[123]" )
		if contact_number:
			return contact_number

	def get_patient(self):
		try:
			patient = Patient.objects.get(contact_number=self.contact_number)
		except Exception, e:
			return None
		return patient


	def get_period(self):
		self.session.streamFile(os.path.join(VOICE_PATH, 'period', '1.wav'))
		period = self.session.playAndGetDigits(
			1, 1, 3, 4000, "",
			os.path.join(VOICE_PATH, 'period', '2.wav'),
			os.path.join(VOICE_PATH, 'fail.wav'),
			"[123]" )
		if period:
			return NUMS_TO_PERIODS[period]

	def get_weight(self):
		weight = self.session.playAndGetDigits(
			2, 5, 3, 4000, "#",
			os.path.join(VOICE_PATH, 'weight', '2.wav'),
			os.path.join(VOICE_PATH, 'fail.wav'),
			"[0-9]*" )                
		if weight:  
			weight_int, weight_dec = re.match(r"(\d+)\*?(\d+)?", weight).group(1), re.match(r"(\d+)\*?(\d+)?", weight).group(2)
			if weight_dec:
				self.weight['weight'] = weight_int + '.' + weight_dec
			else:
				self.weight['weight'] = weight_int
			return self.weight
	
	def get_pressure(self):
		pressure_up = self.session.playAndGetDigits(
			2, 3, 3, 4000, "#",
			os.path.join(VOICE_PATH, 'pressure', '2.wav'),
			os.path.join(VOICE_PATH, 'fail.wav'),
			"[0-9]" )                
		if pressure_up:  
			self.session.sleep(1000)
			pressure_down = self.session.playAndGetDigits(
				2, 3, 3, 4000, "#",
				os.path.join(VOICE_PATH, 'pressure', '3.wav'),
				os.path.join(VOICE_PATH, 'fail.wav'),
				"" )     
			if pressure_down:
				self.pressure['up'] = pressure_up
				self.pressure['down'] = pressure_down
				return self.pressure

	def get_drug(self):
		drug_size = self.session.playAndGetDigits(
			1, 5, 3, 4000, "#",
			os.path.join(VOICE_PATH, 'drug', '2.wav'),
			os.path.join(VOICE_PATH, 'fail.wav'),
			"[0-9]" )                
		if drug_size:  
			self.session.sleep(1000)
			drug_amount = self.session.playAndGetDigits(
				1, 5, 3, 4000, "#",
				os.path.join(VOICE_PATH, 'drug', '3.wav'),
				os.path.join(VOICE_PATH, 'fail.wav'),
				"" )     
			if drug_amount:
				drug_amount_int, drug_amount_dec = re.match(r"(\d+)\*?(\d+)?", drug_amount).group(1), re.match(r"(\d+)\*?(\d+)?", drug_amount).group(2)
				if drug_amount_dec:
					self.drug['amount'] = drug_amount_int + '.' + drug_amount_dec
				else:
					self.drug['amount'] = drug_amount_int
				self.drug['name'] = DRUG_NAMES['l']
				self.drug['size'] = drug_size
				return self.drug

	def get_voicemail(self):
		filename = str(datetime.datetime.now().date()) + "_" + str(datetime.datetime.now().strftime("%H-%M-%S")) + "_" + self.contact_number + ".wav"
		file_path = os.path.join(PROJECT_PATH, 'media', 'voices', 'voicemails', filename)
		self.session.streamFile(os.path.join(VOICE_PATH, 'voicemail', '2.wav'))
		self.session.execute("sleep", "1500")
		self.session.streamFile(os.path.join(VOICE_PATH, 'voicemail', '3.wav'))
		#self.session.setInputCallback(self.input_callback_record_file_pound_stop)
		self.session.recordFile(file_path, 240, 500, 4) 
		self.voicemail['path'] = filename
		return self.voicemail




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

		print patient, weight, patient.get_today_submitted_periods(entry='weight')

		if period == '':
			html_messages = 'ท่านทำรายการไม่ถูกต้อง'
			messages = ["ท่านทำรายการไม่ถูกต้อง"]
		elif weight and period in patient.get_today_submitted_periods(entry='weight'):
			html_messages = 'ท่านได้ส่งข้อมูลน้ำหนักของช่วงเวลานี้แล้ว'
			messages = ["ท่านได้ส่งข้อมูลน้ำหนักของช่วงเวลานี้แล้ว"]
		elif pressure and period in patient.get_today_submitted_periods(entry='pressure'):
			html_messages = 'ท่านได้ส่งข้อมูลความดันของช่วงเวลานี้แล้ว'
			messages = ["ท่านได้ส่งข้อมูลความดันของช่วงเวลานี้แล้ว"]
		elif drug and period in patient.get_today_submitted_periods(entry='drug'):
			html_messages = 'ท่านได้ส่งข้อมูลยาของช่วงเวลานี้แล้ว'
			messages =  ["ท่านได้ส่งข้อมูลยาของช่วงเวลานี้แล้ว"]
		elif not weight and not pressure and not drug:
			html_messages = 'ผิดพลาด ท่านไม่ได้ใส่ข้อมูลเลย กรุณาใส่ข้อมูล'
			messages =  ["ผิดพลาด ท่านไม่ได้ใส่ข้อมูลเลย กรุณาใส่ข้อมูล"]
		else:
			record = patient.create_new_record()
			entry_messages = "p:" + PERIODS[period] + " "
			if weight:
				weight_entry = record.create_entry_for_record_from_voip(period, weight=weight)
				entry_messages = entry_messages + "w" + str(weight_entry.weight) + " "
			if pressure:
				pressure_entry = record.create_entry_for_record_from_voip(period, pressure=pressure)
				entry_messages = entry_messages + "bp" + str(pressure_entry.up)+"/"+ str(pressure_entry.down) + " "
			if drug:
				drug_entry = record.create_entry_for_record_from_voip(period, drug=drug)
				entry_messages = entry_messages + "l" + str(drug_entry.size)+"mg"+ str(drug_entry.amount) + " "
			messages =  ["Ref:"+ str(record.id) +" " + entry_messages]
			html_messages = render_to_string('email/confirm_record.html', { 'record': record })
			record.status = "รอการตอบกลับ และยังไม่ได้รับ SMS ยืนยัน"
			record.save()
		
		send_messages_to_patient(patient.confirm_by, patient.contact_number, patient.email, messages, html_messages)
			
