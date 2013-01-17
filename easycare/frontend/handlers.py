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
		self.session.streamFile(os.path.join(VOICE_PATH, 'share', 'welcome.mp3'))
		self.session.sleep(1000)
		next_menu = self.login_menu(self.period)
		while next_menu:
			next_menu = next_menu(self.period)
		self.session.streamFile(os.path.join(VOICE_PATH, 'share', 'fail.mp3'))
		self.session.streamFile(os.path.join(VOICE_PATH, 'share', 'thankyou.mp3'))
		self.session.destroy()

	def login_menu(self, period):
		self.__init__(self.session)
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
			#end call
			self.session.destroy()

	def period_menu(self, period): #must have 2 arguemnts because while loop
		self.period = self.get_period()
		if self.period in ['morning', 'afternoon', 'evening']:
			return self.weight_menu

	def weight_menu(self, period):
		self.session.streamFile(os.path.join(VOICE_PATH, 'weight', '1-'+ period +'.mp3'))
		weight = self.get_weight()
		if weight:
			response = self.session.playAndGetDigits(
				1, 1, 2, 4000, "",
				os.path.join(VOICE_PATH, 'share', 'confirm.mp3'),
				os.path.join(VOICE_PATH, 'share', 'fail.mp3'),
				"[12]")          
			if response == "1":
				return self.drug_size_menu
			elif response == "2":
				return self.weight_menu

	def drug_size_menu(self, period):
		#hardcode drug name
		self.drug['name'] = DRUG_NAMES['l']

		self.session.streamFile(os.path.join(VOICE_PATH, 'drug', '1-'+ period +'.mp3'))
		drug_size = self.get_drug_size()
		if drug_size:
			response = self.session.playAndGetDigits(
				1, 1, 2, 4000, "",
				os.path.join(VOICE_PATH, 'share', 'confirm.mp3'),
				os.path.join(VOICE_PATH, 'share', 'fail.mp3'),
				"[12]")          
			if response == "1":
				return self.drug_amount_menu
			elif response == "2":
				return self.drug_size_menu

	def drug_amount_menu(self, period):
		drug_amount = self.get_drug_amount()
		if drug_amount:
			response = self.session.playAndGetDigits(
				1, 1, 2, 4000, "",
				os.path.join(VOICE_PATH, 'share', 'confirm.mp3'),
				os.path.join(VOICE_PATH, 'share', 'fail.mp3'),
				"[12]")          
			if response == "1":
				return self.pressure_menu
			elif response == "2":
				return self.drug_amount_menu

	def pressure_menu(self, period):
		response = self.session.playAndGetDigits(
			1, 1, 2, 4000, "",
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
				1, 1, 2, 4000, "",
				os.path.join(VOICE_PATH, 'share', 'confirm.mp3'),
				os.path.join(VOICE_PATH, 'share', 'fail.mp3'),
				"[12]")          
			if response == "1":
				return self.pressure_down_menu
			elif response == "2":
				return self.pressure_up_menu

	def pressure_down_menu(self, period):
		pressure_down = self.get_pressure_down()
		if pressure_down:
			response = self.session.playAndGetDigits(
				1, 1, 2, 4000, "",
				os.path.join(VOICE_PATH, 'share', 'confirm.mp3'),
				os.path.join(VOICE_PATH, 'share', 'fail.mp3'),
				"[12]")          
			if response == "1":
				return self.voicemail_menu
			elif response == "2":
				return self.pressure_down_menu

	def voicemail_menu(self, period):
		response = self.session.playAndGetDigits(
			1, 1, 2, 4000, "",
			os.path.join(VOICE_PATH, 'voicemail', '1.mp3'),
			os.path.join(VOICE_PATH, 'share', 'fail.mp3'),
			"[12]")
		if response == "1":
			voicemail = self.get_voicemail()
			if voicemail:
				return self.conclude_menu
		elif response == "2":
			return self.conclude_menu


	def save_menu(self, period):
		patient = self.get_patient()
		contact_number = patient.contact_number
		weight = self.weight
		pressure = self.pressure
		drug = self.drug
		voicemail = self.voicemail

		if weight and period in patient.get_today_submitted_periods(entry='weight'):
			submitted_record = Record.objects.get( datetime__gte=datetime.date.today(), weight__period=period)
			html_messages = render_to_string('email/confirm_record.html', { 'HEADER':'ท่านได้ส่งข้อมูลน้ำหนักของช่วงเวลานี้แล้ว ตามประวัติด้านล่าง','record': submitted_record })
			messages = "ท่านได้ส่งข้อมูลน้ำหนักของช่วงเวลานี้แล้ว "
		elif pressure and period in patient.get_today_submitted_periods(entry='pressure'):
			submitted_record = Record.objects.get( datetime__gte=datetime.date.today(), pressure__period=period)
			html_messages = render_to_string('email/confirm_record.html', { 'HEADER':'ท่านได้ส่งข้อมูลความดันของช่วงเวลานี้แล้ว ตามประวัติด้านล่าง','record': submitted_record })
			messages = "ท่านได้ส่งข้อมูลความดันของช่วงเวลานี้แล้ว"
		elif drug and period in patient.get_today_submitted_periods(entry='drug'):
			submitted_record = Record.objects.get( datetime__gte=datetime.date.today(), drug__period=period)
			html_messages = render_to_string('email/confirm_record.html', { 'HEADER':'ท่านได้ส่งข้อมูลยาของช่วงเวลานี้แล้ว ตามประวัติด้านล่าง','record': submitted_record })
			messages =  "ท่านได้ส่งข้อมูลยาของช่วงเวลานี้แล้ว"
		else:
			record = patient.create_new_record()
			entry_messages = "p:" + PERIODS[period] + " "
			if weight:
				weight_entry = record.create_entry_for_record_from_voip(period, weight=weight)
				entry_messages = entry_messages + "w:" + str(weight_entry.weight) + " "
			if drug:
				drug_entry = record.create_entry_for_record_from_voip(period, drug=drug)
				entry_messages = entry_messages + "l:" + str(drug_entry.size)+"mg"+ str(drug_entry.amount) + " "
			if pressure:
				pressure_entry = record.create_entry_for_record_from_voip(period, pressure=pressure)
				entry_messages = entry_messages + "bp:" + str(pressure_entry.up)+"/"+ str(pressure_entry.down) + " "
			if voicemail:
				record.voicemail = voicemail['path']
				record.save()
			messages =  "#"+ str(record.id) +" " + entry_messages
			html_messages = render_to_string('email/confirm_record.html', { 'record': record, 'MEDIA_URL':'http://easycare.sit.kmutt.ac.th/media/' })
		sent = send_messages_to_patient(patient.confirm_by, patient.contact_number, patient.email, messages, html_messages)
		if not sent:
			record.status = "รอการตอบกลับ และยังไม่ได้รับ SMS ยืนยัน"
			record.save()

		#end the call
		self.session.destroy()


	def conclude_menu(self, period):
		self.session.streamFile(os.path.join(VOICE_PATH, 'conclude', '1-'+period+'.mp3'))
		self.session.streamFile(os.path.join(VOICE_PATH, 'conclude', '2.mp3'))
		return self.save_menu
		

	def get_contact_number(self):
		contact_number = self.session.playAndGetDigits(
			8, 15, 2, 4000, "#",
			os.path.join(VOICE_PATH, 'login', '1.mp3'),
			os.path.join(VOICE_PATH, 'share', 'fail.mp3'),
			"" )
		if contact_number:
			return contact_number

	def get_patient(self):
		try:
			patient = Patient.objects.get(contact_number=self.contact_number)
		except Exception, e:
			return None
		return patient


	def get_period(self):
		self.session.streamFile(os.path.join(VOICE_PATH, 'period', '1.mp3'))
		period = self.session.playAndGetDigits(
			1, 1, 2, 4000, "",
			os.path.join(VOICE_PATH, 'period', '2.mp3'),
			os.path.join(VOICE_PATH, 'share', 'fail.mp3'),
			"[123]" )
		if period:
			return NUMS_TO_PERIODS[period]

	def get_weight(self):
		weight = self.session.playAndGetDigits(
			2, 7, 2, 4000, "#",
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
	

	def get_drug_size(self):
		drug_size = self.session.playAndGetDigits(
			1, 5, 2, 4000, "#",
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


	def get_drug_amount(self):
		drug_amount = self.session.playAndGetDigits(
			1, 5, 2, 4000, "#",
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


	def get_pressure_up(self):
		pressure_up = self.session.playAndGetDigits(
			2, 5, 2, 4000, "#",
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

	def get_pressure_down(self):
		pressure_down = self.session.playAndGetDigits(
			2, 5, 2, 4000, "#",
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
			html_messages = 'ท่านทำรายการไม่ถูกต้อง'
			messages = "ท่านทำรายการไม่ถูกต้อง"
		elif weight and period in patient.get_today_submitted_periods(entry='weight'):
			submitted_record = Record.objects.get( datetime__gte=datetime.date.today(), weight__period=period)
			html_messages = render_to_string('email/confirm_record.html', { 'HEADER':'ท่านได้ส่งข้อมูลน้ำหนักของช่วงเวลานี้แล้ว ตามประวัติด้านล่าง','record': submitted_record })
			messages = "ท่านได้ส่งข้อมูลน้ำหนักของช่วงเวลานี้แล้ว"
		elif pressure and period in patient.get_today_submitted_periods(entry='pressure'):
			submitted_record = Record.objects.get( datetime__gte=datetime.date.today(), pressure__period=period)
			html_messages = render_to_string('email/confirm_record.html', { 'HEADER':'ท่านได้ส่งข้อมูลความดันของช่วงเวลานี้แล้ว ตามประวัติด้านล่าง','record': submitted_record })
			messages = "ท่านได้ส่งข้อมูลความดันของช่วงเวลานี้แล้ว"
		elif drug and period in patient.get_today_submitted_periods(entry='drug'):
			submitted_record = Record.objects.get( datetime__gte=datetime.date.today(), drug__period=period)
			html_messages = render_to_string('email/confirm_record.html', { 'HEADER':'ท่านได้ส่งข้อมูลยาของช่วงเวลานี้แล้ว ตามประวัติด้านล่าง','record': submitted_record })
			messages =  "ท่านได้ส่งข้อมูลยาของช่วงเวลานี้แล้ว"
		elif not weight and not pressure and not drug:
			html_messages = "ผิดพลาด ท่านไม่ได้ใส่ข้อมูลเลย กรุณาใส่ข้อมูล"
			messages =  "ผิดพลาด ท่านไม่ได้ใส่ข้อมูลเลย กรุณาใส่ข้อมูล"
		else:
			record = patient.create_new_record()
			entry_messages = "p:" + PERIODS[period] + " "
			if weight:
				weight_entry = record.create_entry_for_record_from_voip(period, weight=weight)
				entry_messages = entry_messages + "w:" + str(weight_entry.weight) + " "
			if drug:
				drug_entry = record.create_entry_for_record_from_voip(period, drug=drug)
				entry_messages = entry_messages + "l:" + str(drug_entry.size)+"mg"+ str(drug_entry.amount) + " "
			if pressure:
				pressure_entry = record.create_entry_for_record_from_voip(period, pressure=pressure)
				entry_messages = entry_messages + "bp:" + str(pressure_entry.up)+"/"+ str(pressure_entry.down) + " "
			messages =  "#"+ str(record.id) +" " + entry_messages
			html_messages = render_to_string('email/confirm_record.html', { 'record': record })
			record.status = "รอการตอบกลับ และยังไม่ได้รับ SMS ยืนยัน"
			record.save()
		
		send_messages_to_patient(patient.confirm_by, patient.contact_number, patient.email, messages, html_messages)
			
