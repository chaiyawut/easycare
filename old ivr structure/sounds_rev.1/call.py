#-*-coding: utf-8 -*-
import re
from frontend.models import *
import os
from frontend.utils.words import *
from easycare.settings import PROJECT_PATH
from frontend.services.send_messages_to_patient import send_messages_to_patient
from django.template.loader import render_to_string

VOICE_PATH = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'services', 'sounds'))

class CallHandler:
	def __init__(self, session):
		self.session = session
		self.contact_number = ''
		self.period = ''
		self.weight = {}
		self.drug = {}
		self.pressure = {}
		self.voicemail = {}
		self.login_attempt = 0

	def main_menu(self):
		self.session.sleep(200)
		self.session.streamFile(os.path.join(VOICE_PATH, 'share', 'welcome.mp3'))
		next_menu = self.login_menu(self.period)
		while next_menu:
			self.session.sleep(1000)
			next_menu = next_menu(self.period)
		self.session.streamFile(os.path.join(VOICE_PATH, 'share', 'fail.mp3'))
		self.session.streamFile(os.path.join(VOICE_PATH, 'share', 'thankyou.mp3'))
		self.session.destroy()

	def login_menu(self, period):
		self.session.sleep(1000)
		self.contact_number = self.get_contact_number()
		storeNumber = Patient.objects.all().values_list('contact_number', flat=True)
		if self.contact_number in storeNumber:
			patient = self.get_patient()
			self.session.sleep(500)
			self.session.streamFile(os.path.join(VOICE_PATH, 'login', 'sawadee.mp3'))
			self.session.sleep(100)
			if patient.sound_for_name:
				self.session.streamFile(str(patient.sound_for_name.path))
			elif os.path.exists(os.path.join(PROJECT_PATH, 'media', 'voices', 'sounds_for_name', patient.hn.replace('/', '_') +'.mp3')):
				self.session.streamFile(str(os.path.join(PROJECT_PATH, 'media', 'voices', 'sounds_for_name', patient.hn.replace('/', '_') +'.mp3')))
			else:
				self.session.streamFile(os.path.join(VOICE_PATH, 'share', 'no_name.mp3'))
			self.session.sleep(1000)
			return self.period_menu
		else:
			self.session.streamFile(os.path.join(VOICE_PATH, 'login', 'user_not_found.mp3'))
			if self.login_attempt < 2:
				self.login_attempt = self.login_attempt + 1
				return self.login_menu
			else:
				self.session.destroy()

	def get_patient(self):
		try:
			patient = Patient.objects.get(contact_number=self.contact_number)
		except Exception, e:
			return None
		return patient

	def get_contact_number(self):
		contact_number = self.session.playAndGetDigits(
			8, 15, 2, 5000, "#",
			os.path.join(VOICE_PATH, 'login', '1.mp3'),
			os.path.join(VOICE_PATH, 'share', 'fail.mp3'),
			"" )
		if contact_number:
			return contact_number

	def period_menu(self, period): #must have 2 arguemnts because while loop
		self.period = self.get_period()
		if self.period in ['morning', 'afternoon', 'evening']:
			return self.weight_menu

	def get_period(self):
		self.session.streamFile(os.path.join(VOICE_PATH, 'period', '1.mp3'))
		period = self.session.playAndGetDigits(
			1, 1, 2, 5000, "",
			os.path.join(VOICE_PATH, 'period', '2.mp3'),
			os.path.join(VOICE_PATH, 'share', 'fail.mp3'),
			"[123]" )
		if period:
			return NUMS_TO_PERIODS[period]

	def weight_menu(self, period):
		self.session.streamFile(os.path.join(VOICE_PATH, 'weight', '1-'+ period +'.mp3'))
		weight = self.get_weight()
		if weight:
			response = self.session.playAndGetDigits(
				1, 1, 2, 5000, "",
				os.path.join(VOICE_PATH, 'share', 'confirm.mp3'),
				os.path.join(VOICE_PATH, 'share', 'fail.mp3'),
				"[12]")          
			if response == "1":
				return self.drug_size_menu
			elif response == "2":
				return self.weight_menu

	def get_weight(self):
		weight = self.session.playAndGetDigits(
			2, 7, 2, 5000, "#",
			os.path.join(VOICE_PATH, 'weight', '2.mp3'),
			os.path.join(VOICE_PATH, 'share', 'fail.mp3'),
			"[0-9]*" )                
		if weight:  
			weight_int, weight_dec = re.match(r"(\d+)\*?(\d+)?", weight).group(1), re.match(r"(\d+)\*?(\d+)?", weight).group(2)
			weight_int_sound_path = os.path.join(VOICE_PATH, 'number', weight_int + '.mp3')
			if weight_dec:
				weight_dec_sound_path = os.path.join(VOICE_PATH, 'number', weight_dec + '.mp3')
			else:
				weight_dec_sound_path = ''
			if os.path.exists(weight_int_sound_path) and os.path.exists(weight_dec_sound_path):
				self.weight['weight'] = weight_int + '.' + weight_dec
				self.session.sleep(200)
				self.session.streamFile(os.path.join(VOICE_PATH, 'weight', '3.mp3'))
				self.session.streamFile(weight_int_sound_path)
				self.session.streamFile(os.path.join(VOICE_PATH, 'share', 'dot.mp3'))
				self.session.streamFile(weight_dec_sound_path)
				self.session.streamFile(os.path.join(VOICE_PATH, 'weight', 'kg.mp3'))
			elif os.path.exists(weight_int_sound_path):
				self.weight['weight'] = weight_int
				self.session.sleep(200)
				self.session.streamFile(os.path.join(VOICE_PATH, 'weight', '3.mp3'))
				self.session.streamFile(weight_int_sound_path)
				self.session.streamFile(os.path.join(VOICE_PATH, 'weight', 'kg.mp3'))
			else:
				self.weight['weight'] = '0'
				self.session.sleep(200)
				self.session.streamFile(os.path.join(VOICE_PATH, 'weight', '3.mp3'))
				self.session.streamFile(os.path.join(VOICE_PATH, 'number', '0.mp3'))
				self.session.streamFile(os.path.join(VOICE_PATH, 'weight', 'kg.mp3'))
			return self.weight

	def drug_size_menu(self, period):
		#hardcode drug name
		self.drug['name'] = DRUG_NAMES['l']

		self.session.streamFile(os.path.join(VOICE_PATH, 'drug', '1-'+ period +'.mp3'))
		drug_size = self.get_drug_size()
		if drug_size:
			response = self.session.playAndGetDigits(
				1, 1, 2, 5000, "",
				os.path.join(VOICE_PATH, 'share', 'confirm.mp3'),
				os.path.join(VOICE_PATH, 'share', 'fail.mp3'),
				"[12]")          
			if response == "1":
				return self.drug_amount_menu
			elif response == "2":
				return self.drug_size_menu

	def get_drug_size(self):
		drug_size = self.session.playAndGetDigits(
			1, 5, 2, 5000, "#",
			os.path.join(VOICE_PATH, 'drug', '2.mp3'),
			os.path.join(VOICE_PATH, 'share', 'fail.mp3'),
			"[0-9]" )  
		drug_size_sound_path = os.path.join(VOICE_PATH, 'number', drug_size + '.mp3')   
		if os.path.exists(drug_size_sound_path):  
			self.drug['size'] = drug_size
			self.session.sleep(200)
			self.session.streamFile(os.path.join(VOICE_PATH, 'drug', '3.mp3'))
			self.session.streamFile(os.path.join(VOICE_PATH, 'number', drug_size + '.mp3'))
			self.session.streamFile(os.path.join(VOICE_PATH, 'drug', 'mg.mp3'))
		else:
			self.drug['size'] = '0'
			self.session.sleep(200)
			self.session.streamFile(os.path.join(VOICE_PATH, 'drug', '3.mp3'))
			self.session.streamFile(os.path.join(VOICE_PATH, 'number', '0.mp3'))
			self.session.streamFile(os.path.join(VOICE_PATH, 'drug', 'mg.mp3'))
		return self.drug['size']


	def drug_amount_menu(self, period):
		drug_amount = self.get_drug_amount()
		if drug_amount:
			response = self.session.playAndGetDigits(
				1, 1, 2, 5000, "",
				os.path.join(VOICE_PATH, 'share', 'confirm.mp3'),
				os.path.join(VOICE_PATH, 'share', 'fail.mp3'),
				"[12]")          
			if response == "1":
				return self.pressure_menu
			elif response == "2":
				return self.drug_amount_menu

	def get_drug_amount(self):
		drug_amount = self.session.playAndGetDigits(
			1, 5, 2, 5000, "#",
			os.path.join(VOICE_PATH, 'drug', '4.mp3'),
			os.path.join(VOICE_PATH, 'share', 'fail.mp3'),
			"[0-9]*" ) 
		if drug_amount:
			drug_amount_int, drug_amount_dec = re.match(r"(\d+)\*?(\d+)?", drug_amount).group(1), re.match(r"(\d+)\*?(\d+)?", drug_amount).group(2)
			drug_amount_int_sound_path = os.path.join(VOICE_PATH, 'number', drug_amount_int + '.mp3')
			if drug_amount_dec:
				drug_amount_dec_sound_path = os.path.join(VOICE_PATH, 'number', drug_amount_dec + '.mp3')
			else:
				drug_amount_dec_sound_path = ''
			if os.path.exists(drug_amount_int_sound_path) and os.path.exists(drug_amount_dec_sound_path):
				self.drug['amount'] = drug_amount_int + '.' + drug_amount_dec
				self.session.sleep(200)
				self.session.streamFile(os.path.join(VOICE_PATH, 'drug', '5.mp3'))
				self.session.streamFile(drug_amount_int_sound_path)
				self.session.streamFile(os.path.join(VOICE_PATH, 'share', 'dot.mp3'))
				self.session.streamFile(drug_amount_dec_sound_path)
				self.session.streamFile(os.path.join(VOICE_PATH, 'drug', 'med.mp3'))
			elif os.path.exists(drug_amount_int_sound_path):
				self.drug['amount'] = drug_amount_int
				self.session.sleep(200)
				self.session.streamFile(os.path.join(VOICE_PATH, 'drug', '5.mp3'))
				self.session.streamFile(drug_amount_int_sound_path)
				self.session.streamFile(os.path.join(VOICE_PATH, 'drug', 'med.mp3'))
			else:
				self.drug['amount'] = '0'
				self.session.sleep(200)
				self.session.streamFile(os.path.join(VOICE_PATH, 'drug', '5.mp3'))
				self.session.streamFile(os.path.join(VOICE_PATH, 'number', '0.mp3'))
				self.session.streamFile(os.path.join(VOICE_PATH, 'drug', 'med.mp3'))
		return self.drug['amount']

	def pressure_menu(self, period):
		response = self.session.playAndGetDigits(
			1, 1, 2, 5000, "",
			os.path.join(VOICE_PATH, 'pressure', '1-'+ period +'.mp3'),
			os.path.join(VOICE_PATH, 'share', 'fail.mp3'),
			"[123]")
		if response == "1":
			return self.pressure_up_menu
		elif response == "2":
			return self.voicemail_menu

	def pressure_up_menu(self, period):
		self.session.streamFile(os.path.join(VOICE_PATH, 'pressure', '2-'+ period +'.mp3'))
		pressure_up = self.get_pressure_up()
		if pressure_up:
			response = self.session.playAndGetDigits(
				1, 1, 2, 5000, "",
				os.path.join(VOICE_PATH, 'share', 'confirm.mp3'),
				os.path.join(VOICE_PATH, 'share', 'fail.mp3'),
				"[12]")          
			if response == "1":
				return self.pressure_down_menu
			elif response == "2":
				return self.pressure_up_menu

	def get_pressure_up(self):
		pressure_up = self.session.playAndGetDigits(
			2, 5, 2, 5000, "#",
			os.path.join(VOICE_PATH, 'pressure', '3.mp3'),
			os.path.join(VOICE_PATH, 'share', 'fail.mp3'),
			"[0-9]" )  
		pressure_up_sound_path = os.path.join(VOICE_PATH, 'number', pressure_up + '.mp3')           
		if os.path.exists(pressure_up_sound_path):  
			self.pressure['up'] = pressure_up
			self.session.sleep(200)
			self.session.streamFile(os.path.join(VOICE_PATH, 'pressure', '4.mp3'))
			self.session.streamFile(pressure_up_sound_path)
			self.session.streamFile(os.path.join(VOICE_PATH, 'pressure', 'mmhg.mp3'))
		else:
			self.pressure['up'] = '0'
			self.session.sleep(200)
			self.session.streamFile(os.path.join(VOICE_PATH, 'pressure', '4.mp3'))
			self.session.streamFile(os.path.join(VOICE_PATH, 'number',  '0.mp3'))
			self.session.streamFile(os.path.join(VOICE_PATH, 'pressure', 'mmhg.mp3'))
		return self.pressure['up']

	def pressure_down_menu(self, period):
		pressure_down = self.get_pressure_down()
		if pressure_down:
			response = self.session.playAndGetDigits(
				1, 1, 2, 5000, "",
				os.path.join(VOICE_PATH, 'share', 'confirm.mp3'),
				os.path.join(VOICE_PATH, 'share', 'fail.mp3'),
				"[12]")          
			if response == "1":
				return self.voicemail_menu
			elif response == "2":
				return self.pressure_down_menu

	def get_pressure_down(self):
		pressure_down = self.session.playAndGetDigits(
			2, 5, 2, 5000, "#",
			os.path.join(VOICE_PATH, 'pressure', '5.mp3'),
			os.path.join(VOICE_PATH, 'share', 'fail.mp3'),
			"[0-9]" ) 
		pressure_down_sound_path = os.path.join(VOICE_PATH, 'number', pressure_down + '.mp3')               
		if os.path.exists(pressure_down_sound_path):  
			self.pressure['down'] = pressure_down
			self.session.sleep(200)
			self.session.streamFile(os.path.join(VOICE_PATH, 'pressure', '6.mp3'))
			self.session.streamFile(os.path.join(VOICE_PATH, 'number', pressure_down + '.mp3'))
			self.session.streamFile(os.path.join(VOICE_PATH, 'pressure', 'mmhg.mp3'))
		else:
			self.pressure['down'] = '0'
			self.session.sleep(200)
			self.session.streamFile(os.path.join(VOICE_PATH, 'pressure', '6.mp3'))
			self.session.streamFile(os.path.join(VOICE_PATH, 'number',  '0.mp3'))
			self.session.streamFile(os.path.join(VOICE_PATH, 'pressure', 'mmhg.mp3'))
		return self.pressure['down']

	def voicemail_menu(self, period):
		response = self.session.playAndGetDigits(
			1, 1, 2, 5000, "",
			os.path.join(VOICE_PATH, 'voicemail', '1.mp3'),
			os.path.join(VOICE_PATH, 'share', 'fail.mp3'),
			"[12]")
		if response == "1":
			voicemail = self.get_voicemail()
			if voicemail:
				return self.conclude_menu
		elif response == "2":
			return self.conclude_menu

	def get_voicemail(self):
		filename = str(datetime.datetime.now().date()) + "_" + str(datetime.datetime.now().strftime("%H-%M-%S")) + "_" + self.contact_number + ".mp3"
		file_path = os.path.join(PROJECT_PATH, 'media', 'voices', 'voicemails', filename)
		self.session.streamFile(os.path.join(VOICE_PATH, 'voicemail', '2.mp3'))
		self.session.execute("sleep", "1500")
		self.session.streamFile(os.path.join(VOICE_PATH, 'share', 'beep.mp3'))
		#self.session.setInputCallback(self.input_callback_record_file_pound_stop)
		self.session.recordFile(file_path, 240, 500, 4) 
		self.voicemail['path'] = filename
		return self.voicemail

	def conclude_menu(self, period):
		self.session.streamFile(os.path.join(VOICE_PATH, 'conclude', '1-'+period+'.mp3'))
		self.session.streamFile(os.path.join(VOICE_PATH, 'conclude', '2.mp3'))
		return self.save_menu

	def save_menu(self, period):
		patient = self.get_patient()
		contact_number = patient.contact_number
		weight = self.weight
		pressure = self.pressure
		drug = self.drug
		voicemail = self.voicemail

		if not patient.check_for_no_duplicate_period(period):
			submitted_records = Record.objects.filter(period=period, datetime__gte=datetime.date.today()).exclude(response__deleted=True)
			html_messages = render_to_string('email/duplicate_records.html', { 'HEADER':'เกิดข้อผิดพลาด! ท่านได้ส่งข้อมูลของช่วงเวลานี้แล้ว','submitted_records': submitted_records })
			messages = "ท่านได้ส่งข้อมูลของช่วงเวลานี้แล้ว "
		else:
			record = patient.create_new_record(period, 'ivr')
			messages = '#' + str(record.id) + ' ช่วง:' + PERIODS[period] + ' '
			if weight:
				weight_entry = record.create_entry_for_record_from_voip(weight=weight)
				messages = messages + "น้ำหนัก:" + str(weight_entry.weight) + " "
			if drug:
				drug_entry = record.create_entry_for_record_from_voip( drug=drug)
				messages = messages + "ยา:" + str(drug_entry.size)+"มก."+ str(drug_entry.amount) + "เม็ด "
			if pressure:
				pressure_entry = record.create_entry_for_record_from_voip( pressure=pressure)
				messages = messages + "ความดัน:" + str(pressure_entry.up)+"/"+ str(pressure_entry.down) + " "
			if voicemail:
				record.voicemail = voicemail['path']
				record.save()
			html_messages = render_to_string('email/confirm_record.html', { 'HEADER':'ระบบบันทึกข้อมูลของท่านเรียบร้อยแล้วค่ะ', 'record': record, 'MEDIA_URL':'http://easycare.sit.kmutt.ac.th/media/' })
		sent = send_messages_to_patient(patient.confirm_by, patient.contact_number, patient.email, messages, html_messages)
		if not sent:
			record.status = "รอการตอบกลับ และยังไม่ได้รับ SMS ยืนยัน"
			record.save()

		#end the call
		self.session.destroy()


		












