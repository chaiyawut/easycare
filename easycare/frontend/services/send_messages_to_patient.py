#-*-coding: utf-8 -*-
from frontend.models import *
from django.core.mail import send_mail, BadHeaderError
from django.core.mail import EmailMultiAlternatives
import string

def send_messages_to_patient(msg_type, contact_number, contact_email, reply_messages, html_messages):
	if msg_type == 'sms' or msg_type == 'both':
		#send sms with KMUTT trunk
		from suds.client import Client
		Key = 'dnLjIPco1OCeOfnGFjI5dgLj8vvrhW'
		Mobile = contact_number
		Message = reply_messages.decode('utf-8')
		url = 'http://cronos.kmutt.ac.th/smswebservice/send.asmx?wsdl'
		client = Client(url)
		response = client.service.SendSMS(Key, Mobile, Message)
		if not response.title() == u'No Error, The Request Is Successful':
			return False
	if msg_type == 'email' or msg_type == 'both':
		try:
			subject, from_email, to = 'สรุปข้อมูลจากคลินิกโรคหัวใจล้มเหลวค่ะ', 'easycare.sit@gmail.com', contact_email
			msg = EmailMultiAlternatives(subject, '', from_email, [to])
			msg.attach_alternative(html_messages, "text/html")
			msg.attach_file('/frontend/templates/email/instruction.pdf')
			msg.send()
		except Exception, e:
			return False	
	try:
		#update month log
		Log.update_month_log(msg_type)
	except Exception, e:
		pass
	return True


"""
try:
	from ESL import *
	con = ESLconnection("202.44.9.119", "8021", "ClueCon")
	if con.connected():
		for message in reply_messages:
			if not len(message.decode('utf-8')) > 70:
				#api = "gsmopen_sendsms gsm01 "+ contact_number + " " + message.decode('utf-8')
				api = "chat SMS|gsm01|"+contact_number+"| "+ message.decode('utf-8')
				con.send("api " + api.encode('utf-8'))
			else:
				#api = "gsmopen_sendsms gsm01 "+ contact_number + " " + message.decode('utf-8')
				api = "chat SMS|gsm01|"+contact_number+"|exceed maximum lenght"
				con.send("api " + api.encode('utf-8'))
		#api = "gsmopen_sendsms gsm01 "+ contact_number + " Thank you. Advance Heart failure Clinic, Chulalongkorn Hospital."
		api = "chat SMS|gsm01|"+contact_number+"|Thank you. Advance Heart failure Clinic, Chulalongkorn Hospital."
		con.send("api " + api.encode('utf-8'))
		con.disconnect()
	else:
		return False
except Exception, e:
	return False
"""



