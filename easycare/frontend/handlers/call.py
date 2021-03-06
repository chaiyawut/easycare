#-*-coding: utf-8 -*-
from frontend.models import *
from frontend.utils.words import *
from frontend.services.send_messages_to_patient import send_messages_to_patient
from django.template.loader import render_to_string
from decimal import Decimal
import re
import datetime
from django.utils import timezone
import pytz
now = timezone.now()#.replace(tzinfo=timezone.get_default_timezone())

#use relative path need 3 symbolic links in freeswitch to import settings
PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..'))
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
		self.session.sleep(100)
		next_menu = self.login_menu(self.period)
		while next_menu:
			self.session.sleep(2500)
			next_menu = next_menu(self.period)

	def endcall_menu(self, period):
		self.session.streamFile(os.path.join(VOICE_PATH, 'error', 'attempt_exceed.mp3'))
		self.session.sleep(500)
		self.session.destroy()

	def login_menu(self, period):
		storeNumber = Patient.objects.all().values_list('contact_number', flat=True)
		self.contact_number = self.get_contact_number()
		if self.contact_number in storeNumber:
			patient = self.get_patient()
			self.session.sleep(500)
			self.session.streamFile(os.path.join(VOICE_PATH, 'login', 'hello.mp3'))
			self.session.sleep(100)
			if patient.sound_for_name:
				self.session.streamFile(str(patient.sound_for_name.path))
			else :
				self.session.streamFile(str(os.path.join(PROJECT_PATH, 'media', 'voices', 'sounds_for_name', patient.hn.replace('/', '_') +'.mp3')))
			return self.period_menu
		else:
			if self.login_attempt < 2:
				self.session.streamFile(os.path.join(VOICE_PATH, 'error', 'user_not_found.mp3'))
				self.login_attempt = self.login_attempt + 1
				return self.login_menu
			else:
				return self.endcall_menu

	def get_contact_number(self):
		contact_number = self.session.playAndGetDigits(
			8, 13, 1, 6000, "#",
			os.path.join(VOICE_PATH, 'login', '1.mp3'),
			"",
			"")
		return contact_number

	def get_patient(self):
		try:
			patient = Patient.objects.get(contact_number=self.contact_number)
		except Exception, e:
			return None
		return patient

	def period_menu(self, period): #must have 2 arguemnts because while loop
		period = self.get_period()
		if period:
			return self.weight_menu
		else:
			return self.endcall_menu

	def get_period(self):
		period = self.session.playAndGetDigits(
			1, 1, 3, 6000, "",
			os.path.join(VOICE_PATH, 'period', '1.mp3'),
			os.path.join(VOICE_PATH, 'error', 'period.mp3'),
			"[123]" )
		if period:
			self.period = NUMS_TO_PERIODS[period]
			return self.period

	def weight_menu(self, period):
		weight = self.get_weight()
		if weight:
			response = self.session.playAndGetDigits(
				1, 1, 3, 6000, "",
				os.path.join(VOICE_PATH, 'share', 'confirm.mp3'),
				os.path.join(VOICE_PATH, 'error', 'confirm.mp3'),
				"[12]")          
			if response == "1":
				return self.drug_size_menu
			elif response == "2":
				return self.weight_menu
			else:
				return self.endcall_menu
		else:
			return self.endcall_menu

	def get_weight(self):
		weight = self.session.playAndGetDigits(
			2, 7, 3, 6000, "#",
			os.path.join(VOICE_PATH, 'weight', '1.mp3'),
			os.path.join(VOICE_PATH, 'error', 'timeout.mp3'),
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
				self.session.streamFile(os.path.join(VOICE_PATH, 'weight', '2.mp3'))
				self.session.streamFile(weight_int_sound_path)
				self.session.streamFile(os.path.join(VOICE_PATH, 'share', 'dot.mp3'))
				self.session.streamFile(weight_dec_sound_path)
				self.session.streamFile(os.path.join(VOICE_PATH, 'weight', 'kg.mp3'))
			elif os.path.exists(weight_int_sound_path):
				self.weight['weight'] = weight_int
				self.session.sleep(200)
				self.session.streamFile(os.path.join(VOICE_PATH, 'weight', '2.mp3'))
				self.session.streamFile(weight_int_sound_path)
				self.session.streamFile(os.path.join(VOICE_PATH, 'weight', 'kg.mp3'))
			else:
				self.weight['weight'] = '0'
				self.session.sleep(200)
				self.session.streamFile(os.path.join(VOICE_PATH, 'weight', '2.mp3'))
				self.session.streamFile(os.path.join(VOICE_PATH, 'number', '0.mp3'))
				self.session.streamFile(os.path.join(VOICE_PATH, 'weight', 'kg.mp3'))
			return self.weight

	def drug_size_menu(self, period):
		self.drug['name'] = DRUG_NAMES['l'] #hardcode drug name
		drug_size = self.get_drug_size()
		if drug_size:
			response = self.session.playAndGetDigits(
				1, 1, 3, 6000, "",
				os.path.join(VOICE_PATH, 'share', 'confirm.mp3'),
				os.path.join(VOICE_PATH, 'error', 'confirm.mp3'),
				"[12]")          
			if response == "1":
				return self.drug_amount_menu
			elif response == "2":
				return self.drug_size_menu
			else:
				return self.endcall_menu
		else:
			return self.endcall_menu

	def get_drug_size(self):
		drug_size = self.session.playAndGetDigits(
			1, 5, 3, 6000, "#",
			os.path.join(VOICE_PATH, 'drug', '1.mp3'),
			os.path.join(VOICE_PATH, 'error', 'timeout.mp3'),
			"[0-9]" )
		if drug_size:
			drug_size_sound_path = os.path.join(VOICE_PATH, 'number', drug_size + '.mp3')   
			if os.path.exists(drug_size_sound_path):  
				self.drug['size'] = drug_size
				self.session.sleep(200)
				self.session.streamFile(os.path.join(VOICE_PATH, 'drug', '2.mp3'))
				self.session.streamFile(os.path.join(VOICE_PATH, 'number', drug_size + '.mp3'))
				self.session.streamFile(os.path.join(VOICE_PATH, 'drug', 'mg.mp3'))
			else:
				self.drug['size'] = '0'
				self.session.sleep(200)
				self.session.streamFile(os.path.join(VOICE_PATH, 'drug', '2.mp3'))
				self.session.streamFile(os.path.join(VOICE_PATH, 'number', '0.mp3'))
				self.session.streamFile(os.path.join(VOICE_PATH, 'drug', 'mg.mp3'))
			return self.drug['size']

	def drug_amount_menu(self, period):
		drug_amount = self.get_drug_amount()
		if drug_amount:
			response = self.session.playAndGetDigits(
				1, 1, 3, 6000, "",
				os.path.join(VOICE_PATH, 'share', 'confirm.mp3'),
				os.path.join(VOICE_PATH, 'error', 'confirm.mp3'),
				"[12]")          
			if response == "1":
				return self.pressure_menu
			elif response == "2":
				return self.drug_amount_menu
			else:
				return self.endcall_menu
		else:
			return self.endcall_menu


	def get_drug_amount(self):
		drug_amount = self.session.playAndGetDigits(
			1, 5, 3, 6000, "#",
			os.path.join(VOICE_PATH, 'drug', '3.mp3'),
			os.path.join(VOICE_PATH, 'error', 'timeout.mp3'),
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
				self.session.streamFile(os.path.join(VOICE_PATH, 'drug', '4.mp3'))
				self.session.streamFile(drug_amount_int_sound_path)
				self.session.streamFile(os.path.join(VOICE_PATH, 'share', 'dot.mp3'))
				self.session.streamFile(drug_amount_dec_sound_path)
				self.session.streamFile(os.path.join(VOICE_PATH, 'drug', 'med.mp3'))
			elif os.path.exists(drug_amount_int_sound_path):
				self.drug['amount'] = drug_amount_int
				self.session.sleep(200)
				self.session.streamFile(os.path.join(VOICE_PATH, 'drug', '4.mp3'))
				self.session.streamFile(drug_amount_int_sound_path)
				self.session.streamFile(os.path.join(VOICE_PATH, 'drug', 'med.mp3'))
			else:
				self.drug['amount'] = '0'
				self.session.sleep(200)
				self.session.streamFile(os.path.join(VOICE_PATH, 'drug', '4.mp3'))
				self.session.streamFile(os.path.join(VOICE_PATH, 'number', '0.mp3'))
				self.session.streamFile(os.path.join(VOICE_PATH, 'drug', 'med.mp3'))
			return self.drug['amount']

	def pressure_menu(self, period):
		response = self.session.playAndGetDigits(
			1, 1, 3, 6000, "",
			os.path.join(VOICE_PATH, 'pressure', '1.mp3'),
			os.path.join(VOICE_PATH, 'error', 'invalid_answer.mp3'),
			"[12]")
		if response == "1":
			return self.pressure_up_menu
		elif response == "2":
			return self.voicemail_menu
		else:
			return self.endcall_menu

	def pressure_up_menu(self, period):
		pressure_up = self.get_pressure_up()
		if pressure_up:
			response = self.session.playAndGetDigits(
				1, 1, 3, 6000, "",
				os.path.join(VOICE_PATH, 'share', 'confirm.mp3'),
				os.path.join(VOICE_PATH, 'error', 'confirm.mp3'),
				"[12]")          
			if response == "1":
				return self.pressure_down_menu
			elif response == "2":
				return self.pressure_up_menu
			else:
				return self.endcall_menu
		else:
			return self.endcall_menu

	def get_pressure_up(self):
		pressure_up = self.session.playAndGetDigits(
			2, 5, 3, 6000, "#",
			os.path.join(VOICE_PATH, 'pressure', '2.mp3'),
			os.path.join(VOICE_PATH, 'error', 'timeout.mp3'),
			"[0-9]" )  
		if pressure_up:
			pressure_up_sound_path = os.path.join(VOICE_PATH, 'number', pressure_up + '.mp3')           
			if os.path.exists(pressure_up_sound_path):  
				self.pressure['up'] = pressure_up
				self.session.sleep(200)
				self.session.streamFile(os.path.join(VOICE_PATH, 'pressure', '3.mp3'))
				self.session.streamFile(pressure_up_sound_path)
				self.session.streamFile(os.path.join(VOICE_PATH, 'pressure', 'mmhg.mp3'))
			else:
				self.pressure['up'] = '0'
				self.session.sleep(200)
				self.session.streamFile(os.path.join(VOICE_PATH, 'pressure', '3.mp3'))
				self.session.streamFile(os.path.join(VOICE_PATH, 'number',  '0.mp3'))
				self.session.streamFile(os.path.join(VOICE_PATH, 'pressure', 'mmhg.mp3'))
			return self.pressure['up']

	def pressure_down_menu(self, period):
		pressure_down = self.get_pressure_down()
		if pressure_down:
			response = self.session.playAndGetDigits(
				1, 1, 3, 6000, "",
				os.path.join(VOICE_PATH, 'share', 'confirm.mp3'),
				os.path.join(VOICE_PATH, 'error', 'confirm.mp3'),
				"[12]")          
			if response == "1":
				return self.voicemail_menu
			elif response == "2":
				return self.pressure_down_menu
			else:
				return self.endcall_menu
		else:
			return self.endcall_menu

	def get_pressure_down(self):
		pressure_down = self.session.playAndGetDigits(
			2, 5, 3, 6000, "#",
			os.path.join(VOICE_PATH, 'pressure', '4.mp3'),
			os.path.join(VOICE_PATH, 'error', 'timeout.mp3'),
			"[0-9]" ) 
		if pressure_down:
			pressure_down_sound_path = os.path.join(VOICE_PATH, 'number', pressure_down + '.mp3')               
			if os.path.exists(pressure_down_sound_path):  
				self.pressure['down'] = pressure_down
				self.session.sleep(200)
				self.session.streamFile(os.path.join(VOICE_PATH, 'pressure', '5.mp3'))
				self.session.streamFile(os.path.join(VOICE_PATH, 'number', pressure_down + '.mp3'))
				self.session.streamFile(os.path.join(VOICE_PATH, 'pressure', 'mmhg.mp3'))
			else:
				self.pressure['down'] = '0'
				self.session.sleep(200)
				self.session.streamFile(os.path.join(VOICE_PATH, 'pressure', '5.mp3'))
				self.session.streamFile(os.path.join(VOICE_PATH, 'number',  '0.mp3'))
				self.session.streamFile(os.path.join(VOICE_PATH, 'pressure', 'mmhg.mp3'))
			return self.pressure['down']

	def voicemail_menu(self, period):
		response = self.session.playAndGetDigits(
			1, 1, 3, 6000, "",
			os.path.join(VOICE_PATH, 'voicemail', '1.mp3'),
			os.path.join(VOICE_PATH, 'error', 'invalid_answer.mp3'),
			"[12]")
		if response == "1":
			voicemail = self.get_voicemail()
			return self.conclude_menu
		elif response == "2":
			return self.conclude_menu
		else:
			return self.endcall_menu

	def get_voicemail(self):
		filename = str(now.date()) + "_" + str(now.strftime("%H-%M-%S")) + "_" + self.contact_number + ".mp3"
		file_path = os.path.join(PROJECT_PATH, 'media', 'voices', 'voicemails', filename)
		self.session.streamFile(os.path.join(VOICE_PATH, 'voicemail', '2.mp3'))
		self.session.sleep(500)
		self.session.streamFile(os.path.join(VOICE_PATH, 'share', 'beep.mp3'))
		self.session.recordFile(file_path, 240, 500, 4) 
		self.voicemail['path'] = filename
		return self.voicemail

	def conclude_menu(self, period):
		self.session.streamFile(os.path.join(VOICE_PATH, 'conclude', '1.mp3'))
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
			submitted_records = patient.record_set.filter( datetime__range=(datetime.datetime.combine(now.date(), datetime.time.min).replace(tzinfo=timezone.get_default_timezone()),
                            datetime.datetime.combine(now.date(), datetime.time.max).replace(tzinfo=timezone.get_default_timezone()))).exclude(response__deleted=True)
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
			html_messages = render_to_string('email/confirm_record.html', { 'record': record, 'MEDIA_URL':'http://easycare.sit.kmutt.ac.th/media/' })
		sent = send_messages_to_patient(patient.confirm_by, patient.contact_number, patient.email, messages, html_messages)
		if not sent:
			record.status = "รอการตอบกลับ และยังไม่ได้รับ SMS ยืนยัน"
			record.save()



		












